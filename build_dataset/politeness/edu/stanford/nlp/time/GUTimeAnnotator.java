
package edu.stanford.nlp.time;

import edu.stanford.nlp.io.IOUtils;
import edu.stanford.nlp.io.RuntimeIOException;
import edu.stanford.nlp.ling.CoreAnnotations;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.pipeline.Annotator;
import edu.stanford.nlp.time.TimeAnnotations.TimexAnnotation;
import edu.stanford.nlp.time.TimeAnnotations.TimexAnnotations;
import edu.stanford.nlp.util.ArrayCoreMap;
import edu.stanford.nlp.util.CoreMap;
import edu.stanford.nlp.util.DataFilePaths;
import edu.stanford.nlp.util.SystemUtils;
import nu.xom.*;

import java.io.File;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.util.*;
import java.util.regex.Pattern;


/**
 * Annotates text using GUTime perl script.
 *
 * GUTIME/TimeML specifications can be found at:
 * <a href="http://www.timeml.org/site/tarsqi/modules/gutime/index.html">
 * http://www.timeml.org/site/tarsqi/modules/gutime/index.html</a>.
 */
public class GUTimeAnnotator implements Annotator {
  
  private static final String BASE_PATH = "$NLP_DATA_HOME/packages/GUTime";
  private static final String DEFAULT_PATH = DataFilePaths.convert(BASE_PATH);
  private final File gutimePath;
  private final boolean outputResults;
  
  // if used in a pipeline or constructed with a Properties object,
  // this property tells the annotator where to find the script
  public static final String GUTIME_PATH_PROPERTY = "gutime.path";
  public static final String GUTIME_OUTPUT_RESULTS = "gutime.outputResults";

  public GUTimeAnnotator() {
    this(new File(System.getProperty("gutime", DEFAULT_PATH)));
  }

  public GUTimeAnnotator(File gutimePath) {
    this.gutimePath = gutimePath;
    this.outputResults = false;
  }

  public GUTimeAnnotator(String name, Properties props) {
    String path = props.getProperty(GUTIME_PATH_PROPERTY,
                                    System.getProperty("gutime", 
                                                       DEFAULT_PATH));
    this.gutimePath = new File(path);

    this.outputResults = 
      Boolean.valueOf(props.getProperty(GUTIME_OUTPUT_RESULTS, "false"));
  }

  public void annotate(Annotation annotation) {
    try {
      this.annotate((CoreMap)annotation);
    } catch (IOException e) {
      throw new RuntimeIOException(e);
    }
  }

  public void annotate(CoreMap document) throws IOException {
    // write input file in GUTime format
    Element inputXML = toInputXML(document);
    File inputFile = File.createTempFile("gutime", ".input");



    //Document doc = new Document(inputXML);
    PrintWriter inputWriter = new PrintWriter(inputFile);
    inputWriter.println(inputXML.toXML());
   // new XMLOutputter().output(inputXML, inputWriter);
    inputWriter.close();

    boolean useFirstDate = 
      (!document.has(CoreAnnotations.CalendarAnnotation.class) && !document.has(CoreAnnotations.DocDateAnnotation.class));
    
    ArrayList<String> args = new ArrayList<String>();
    args.add("perl");
    args.add("-I" + this.gutimePath.getPath());
    args.add(new File(this.gutimePath, "TimeTag.pl").getPath());
    if (useFirstDate)
      args.add("-FDNW");
    args.add(inputFile.getPath());
    // run GUTime on the input file
    ProcessBuilder process = new ProcessBuilder(args);

    StringWriter outputWriter = new StringWriter();
    SystemUtils.run(process, outputWriter, null);
    String output = outputWriter.getBuffer().toString();
    Pattern docClose = Pattern.compile("</DOC>.*", Pattern.DOTALL);
    output = docClose.matcher(output).replaceAll("</DOC>");

    // parse the GUTime output
    Element outputXML;
    try {
      Document newNodeDocument = new Builder().build(output, "");
      outputXML = newNodeDocument.getRootElement();
    } catch (ParsingException ex) {
      throw new RuntimeException(String.format("error:\n%s\ninput:\n%s\noutput:\n%s",
      		ex, IOUtils.slurpFile(inputFile), output));
    }
    /*
    try {
      outputXML = new SAXBuilder().build(new StringReader(output)).getRootElement();
    } catch (JDOMException e) {
      throw new RuntimeException(String.format("error:\n%s\ninput:\n%s\noutput:\n%s",
      		e, IOUtils.slurpFile(inputFile), output));
    } */
    inputFile.delete();
    
    // get Timex annotations
    List<CoreMap> timexAnns = toTimexCoreMaps(outputXML, document);
    document.set(TimexAnnotations.class, timexAnns);
    if (outputResults) {
      System.out.println(timexAnns);
    }
    
    // align Timex annotations to sentences
    int timexIndex = 0;
    for (CoreMap sentence: document.get(CoreAnnotations.SentencesAnnotation.class)) {
    	int sentBegin = beginOffset(sentence);
    	int sentEnd = endOffset(sentence);
    	
    	// skip times before the sentence
    	while (timexIndex < timexAnns.size() && beginOffset(timexAnns.get(timexIndex)) < sentBegin) {
    		++timexIndex;
    	}
    	
    	// determine times within the sentence
    	int sublistBegin = timexIndex;
    	int sublistEnd = timexIndex;
    	while (timexIndex < timexAnns.size() &&
    			   sentBegin <= beginOffset(timexAnns.get(timexIndex)) &&
    			   endOffset(timexAnns.get(timexIndex)) <= sentEnd) {
    		++sublistEnd;
    		++timexIndex;
    	}
    	
    	// set the sentence timexes
    	sentence.set(TimexAnnotations.class, timexAnns.subList(sublistBegin, sublistEnd));
    }
  }
  
  private static int beginOffset(CoreMap ann) {
  	return ann.get(CoreAnnotations.CharacterOffsetBeginAnnotation.class);
  }
  
  private static int endOffset(CoreMap ann) {
  	return ann.get(CoreAnnotations.CharacterOffsetEndAnnotation.class);
  }
  
  private static Element toInputXML(CoreMap document) {
    // construct GUTime format XML
    Element doc = new Element("DOC");
    doc.appendChild("\n");
    // populate the date element
    Calendar dateCalendar = 
      document.get(CoreAnnotations.CalendarAnnotation.class);
    if (dateCalendar != null) {
      Element date = new Element("date");
      date.appendChild(String.format("%TF", dateCalendar));
      doc.appendChild(date);
      doc.appendChild("\n");
    } else {
      String s = document.get(CoreAnnotations.DocDateAnnotation.class);
      if (s != null) {
        Element date = new Element("date");
        date.appendChild(s);
        doc.appendChild(date);
        doc.appendChild("\n");
      }
    }
    Element textElem = new Element("text");
    doc.appendChild(textElem);
    doc.appendChild("\n");
    
    // populate the text element
    String text = document.get(CoreAnnotations.TextAnnotation.class);
    int offset = 0;
    for (CoreMap sentence: document.get(CoreAnnotations.SentencesAnnotation.class)) {
      int sentBegin = sentence.get(CoreAnnotations.CharacterOffsetBeginAnnotation.class);
      int sentEnd = sentence.get(CoreAnnotations.CharacterOffsetEndAnnotation.class);
      
      // add text before the first token
      textElem.appendChild(text.substring(offset, sentBegin));
      offset = sentBegin;
      
      // add one "s" element per sentence
      Element s = new Element("s");
      textElem.appendChild(s);
      for (CoreLabel token: sentence.get(CoreAnnotations.TokensAnnotation.class)) {
        int tokenBegin = token.get(CoreAnnotations.CharacterOffsetBeginAnnotation.class);
        int tokenEnd = token.get(CoreAnnotations.CharacterOffsetEndAnnotation.class);
        s.appendChild(text.substring(offset, tokenBegin));
        offset = tokenBegin;
        
        // add one "lex" element per token
        Element lex = new Element("lex");
        s.appendChild(lex);
        String posTag = 
          token.get(CoreAnnotations.PartOfSpeechAnnotation.class);
        if (posTag != null){
          lex.addAttribute(new Attribute("pos", posTag));
        }
        assert token.word().equals(text.substring(offset, tokenEnd));
        lex.appendChild(text.substring(offset, tokenEnd));
        offset = tokenEnd;
      }
      
      // add text after the last token
      textElem.appendChild(text.substring(offset, sentEnd));
      offset = sentEnd;
    }
    
    // add text after the last sentence
    textElem.appendChild(text.substring(offset, text.length()));
    
    // return the document
    return doc;
  }
  
  private static List<CoreMap> toTimexCoreMaps(Element docElem, CoreMap originalDocument) {
    //--Collect Token Offsets 
    HashMap<Integer,Integer> beginMap = new HashMap<Integer,Integer>();
    HashMap<Integer,Integer> endMap = new HashMap<Integer,Integer>();
    boolean haveTokenOffsets = true;
    for(CoreMap sent : originalDocument.get(CoreAnnotations.SentencesAnnotation.class)){
      for(CoreLabel token : sent.get(CoreAnnotations.TokensAnnotation.class)){
        Integer tokBegin = token.get(CoreAnnotations.TokenBeginAnnotation.class);
        Integer tokEnd = token.get(CoreAnnotations.TokenEndAnnotation.class);
        if(tokBegin == null || tokEnd == null){ haveTokenOffsets = false; }
        int charBegin = token.get(CoreAnnotations.CharacterOffsetBeginAnnotation.class);
        int charEnd = token.get(CoreAnnotations.CharacterOffsetEndAnnotation.class);
        beginMap.put(charBegin,tokBegin);
        endMap.put(charEnd,tokEnd);
      }
    }
    //--Set Timexes
    List<CoreMap> timexMaps = new ArrayList<CoreMap>();
    int offset = 0;
    Element textElem = docElem.getFirstChildElement("text");
    for (int i = 0; i < textElem.getChildCount(); i++) {
      Node content = textElem.getChild(i);
      if (content instanceof Text) {
        Text text = (Text)content;
        offset += text.getValue().length();
      } else if (content instanceof Element) {
        Element child = (Element)content;
        if (child.getLocalName().equals("TIMEX3")) {
          Timex timex = new Timex(child);
          if (child.getChildCount() != 1) {
            throw new RuntimeException("TIMEX3 should only contain text " + child);
          }
          String timexText = child.getValue();
          CoreMap timexMap = new ArrayCoreMap();
          //(timex)
          timexMap.set(TimexAnnotation.class, timex);
          //(text)
          timexMap.set(CoreAnnotations.TextAnnotation.class, timexText);
          //(characters)
          int charBegin = offset;
          timexMap.set(CoreAnnotations.CharacterOffsetBeginAnnotation.class, charBegin);
          offset += timexText.length();
          int charEnd = offset;
          timexMap.set(CoreAnnotations.CharacterOffsetEndAnnotation.class, charEnd);
          //(tokens)
          if(haveTokenOffsets){
            Integer tokBegin = beginMap.get(charBegin);
            int searchStep = 1;          //if no exact match, search around the character offset
            while(tokBegin == null){
              tokBegin = beginMap.get(charBegin - searchStep);
              if(tokBegin == null){
                tokBegin = beginMap.get(charBegin + searchStep);
              }
              searchStep += 1;
            }
            searchStep = 1;
            Integer tokEnd = endMap.get(charEnd);
            while(tokEnd == null){
              tokEnd = endMap.get(charEnd - searchStep);
              if(tokEnd == null){
                tokEnd = endMap.get(charEnd + searchStep);
              }
              searchStep += 1;
            }
            timexMap.set(CoreAnnotations.TokenBeginAnnotation.class, tokBegin);
            timexMap.set(CoreAnnotations.TokenEndAnnotation.class, tokEnd);
          }
          //(add)
          timexMaps.add(timexMap);
        } else {
          throw new RuntimeException("unexpected element " + child);
        }
      } else {
        throw new RuntimeException("unexpected content " + content);
      }
    }
    return timexMaps;
  }
}

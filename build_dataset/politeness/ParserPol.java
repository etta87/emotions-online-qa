
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.Properties;

import edu.stanford.*;
import edu.stanford.nlp.dcoref.CorefChain;
import edu.stanford.nlp.dcoref.CorefCoreAnnotations.CorefChainAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.NamedEntityTagAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.PartOfSpeechAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.SentencesAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.TextAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.TokensAnnotation;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.Sentence;
import edu.stanford.nlp.ling.tokensregex.SequencePattern.Parser;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.pipeline.ParserAnnotator;
import edu.stanford.nlp.pipeline.ParserAnnotatorUtils;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.trees.GrammaticalStructure;
import edu.stanford.nlp.trees.GrammaticalStructureFactory;
import edu.stanford.nlp.trees.PennTreebankLanguagePack;
import edu.stanford.nlp.trees.Tree;
import edu.stanford.nlp.trees.TreePrint;
import edu.stanford.nlp.trees.TreebankLanguagePack;
import edu.stanford.nlp.trees.TreeCoreAnnotations.TreeAnnotation;
import edu.stanford.nlp.trees.semgraph.SemanticGraph;
import edu.stanford.nlp.trees.semgraph.SemanticGraphCoreAnnotations.CollapsedCCProcessedDependenciesAnnotation;
import edu.stanford.nlp.trees.semgraph.SemanticGraphFormatter;
import edu.stanford.nlp.util.CoreMap;



class ParserPol {
	
	public ParserPol () {
		// TODO Auto-generated constructor stub
		super();
		
	}

	public String[] parsing (String text) 
	{
		// creates a StanfordCoreNLP object, with POS tagging, lemmatization, NER, parsing, 
		// and coreference resolution 
		String parser[]= null;
		Properties props = new Properties();
		//props.put("annotators", "tokenize, ssplit, pos, lemma, ner, parse, dcoref");
		props.put("annotators", "tokenize, ssplit, pos, parse");
		StanfordCoreNLP pipeline = new StanfordCoreNLP(props);
    
		// read some text in the text variable
		//String text = " "; // Add your text here!
    
		// create an empty Annotation just with the given text
		Annotation document = new Annotation(text);
    
		// run all Annotators on this text
		pipeline.annotate(document);
    
		// these are all the sentences in this document
		// a CoreMap is essentially a Map that uses class objects as keys and has values with custom types
		List<CoreMap> sentences = document.get(SentencesAnnotation.class);
    
		for(CoreMap sentence: sentences)
		{
			// traversing the words in the current sentence
			// a CoreLabel is a CoreMap with additional token-specific methods
			for (CoreLabel token: sentence.get(TokensAnnotation.class))
			{
				// this is the text of the token
				String word = token.get(TextAnnotation.class);
				//System.out.println("Word: "+word);
				// this is the POS tag of the token
				String pos = token.get(PartOfSpeechAnnotation.class);
				//System.out.println("Pos: "+pos);
				// this is the NER label of the token
				String ne = token.get(NamedEntityTagAnnotation.class); 
				//System.out.println("Ne: "+ne);
			}

			// this is the parse tree of the current sentence
			Tree tree = sentence.get(TreeAnnotation.class);
			//tree.pennPrint();
			//System.out.println();
      
			TreebankLanguagePack tlp = new PennTreebankLanguagePack();
			GrammaticalStructureFactory gsf = tlp.grammaticalStructureFactory();
			GrammaticalStructure gs = gsf.newGrammaticalStructure(tree);
			Collection tdl = gs.typedDependenciesCollapsed();
			//System.out.println("ECCO L'OUTPUT ->");
			Object pars[]=tdl.toArray();
			parser= new String[pars.length];
			//System.out.println(pars.length);
      
			for (int i=0;i<pars.length;i++)
			{
				parser[i]= pars[i].toString();
			}
      
			/*for (int i=0;i<parser.length;i++)
			{
				System.out.println(parser[i]);
			}*/
      
			//System.out.println(tdl);
			//System.out.println("FINE OUT");

      
			//TreePrint tp = new TreePrint("penn,typedDependenciesCollapsed");
			//TreePrint tp1 = new TreePrint("typedDependencies");
			//tp.printTree(parse);
			//tp1.printTree(tree);
      
            //System.out.println(tree);
      
			// this is the Stanford dependency graph of the current sentence
			//SemanticGraph dependencies = sentence.get(CollapsedCCProcessedDependenciesAnnotation.class);
			// System.out.println(dependencies);
      
      
		}

		// This is the coreference link graph
		// Each chain stores a set of mentions that link to each other,
		// along with a method for getting the most representative mention
		// Both sentence and token offsets start at 1!
		//Map<Integer, CorefChain> graph = document.get(CorefChainAnnotation.class);
		// System.out.println(graph);
		//System.out.println("bbbbb "+graph.get(1));
    
    
		//ParserAnnotator parser = Sentence.ex.extractNgram(arg0, arg1, arg2)
		//ParserAnnotatorUtils.fillInParseAnnotations(true, sentence, tree); 
	      return parser;
	}


	
	public static void main(String[] args) {
		// TODO Auto-generated method stub
		//parsing ("The strongest rain ever recorded in India shut down the financial hub of Mumbai, snapped communication lines, closed airports and forced thousands of people to sleep in their offices or walk home during the night, officials said today.");
		//String[] out=parsing("why wasn't it moved?");
		
		//for (int i=0;i<out.length;i++)
		//{
		//	System.out.println(out[i]);
		//}
  
	}
	

}
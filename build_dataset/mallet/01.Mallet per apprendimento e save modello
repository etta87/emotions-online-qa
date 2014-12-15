/*
 * Codice sorgente java per creare Mallet10T.jar (per apprendimento del modello, question tag e save del modello con relative info tra cui il LL/N°TOKEN) 
 *
 * Prende in input il file csv che ha due campi:
 * 		- 'PostId': id del post
 * 		- 'Corpus': campo che contiene il testo da analizzare
 *
 * Scrive in output il file csv con i campi:
 * 		- 'PostId': id del post
 * 		- 'Topic0': score del post per il topic 0
 * 		- 'TopicN': score del post per il topic N
 *
 */

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.ObjectOutputStream;
import java.io.Reader;
import java.io.Writer;
import java.util.ArrayList;
import java.util.Formatter;
import java.util.Locale;
import java.util.regex.Pattern;

import stemming.Snowball;
import cc.mallet.pipe.CharSequence2TokenSequence;
import cc.mallet.pipe.CharSequenceLowercase;
import cc.mallet.pipe.Pipe;
import cc.mallet.pipe.SerialPipes;
import cc.mallet.pipe.TokenSequence2FeatureSequence;
import cc.mallet.pipe.TokenSequenceNGrams;
import cc.mallet.pipe.TokenSequenceRemoveStopwords;
import cc.mallet.pipe.iterator.CsvIterator;
import cc.mallet.topics.ParallelTopicModel;
import cc.mallet.types.Alphabet;
import cc.mallet.types.FeatureSequence;
import cc.mallet.types.Instance;
import cc.mallet.types.InstanceList;
import cc.mallet.types.LabelSequence;
import csv.CSVFormat;
import csv.CSVIterator;
import csv.CSVPrinter;
import csv.CSVRecord;


public class Mallet {

	public Mallet() {
		// TODO Auto-generated constructor stub
	}

	public static void topics(String inputFile, String outputFile, String stopwords, String modelfile, String llfile, int n_topics, int iter, boolean with_stemming) throws IOException, ClassNotFoundException, InstantiationException, IllegalAccessException{
		// Begin by importing documents from text to feature sequences
        ArrayList<Pipe> pipeList = new ArrayList<Pipe>();

        // Pipes: lowercase, tokenize, remove stopwords, map to features
        
        pipeList.add( new CharSequenceLowercase() );
        pipeList.add( new CharSequence2TokenSequence(Pattern.compile("\\p{L}[\\p{L}\\p{P}]+\\p{L}")) );
        //pipeList.add( new TokenSequenceRemoveStopwords(new File("lib/mallet-2.0.7/stoplists/en.txt"), "UTF-8", false, false, false) );
        pipeList.add( new TokenSequenceRemoveStopwords(new File(stopwords), "UTF-8", false, false, false) );
        pipeList.add(new TokenSequenceNGrams(new int[] {1,2} )); //Bigram
        pipeList.add( new TokenSequence2FeatureSequence() );

        InstanceList instances = new InstanceList (new SerialPipes(pipeList));

        
        //Reader fileReader = new InputStreamReader(new FileInputStream(new File(inputFile)), "UTF-8");
        /*instances.addThruPipe(new CsvIterator (fileReader, Pattern.compile("^(\\S*)[\\s,]*(\\S*)[\\s,]*(\\S*)[\\s,]*(\\S*)[\\s,]*(.*)"),
                                               3, 0, 0)); // data, label, name fields*/
        CSVIterator it = new CSVIterator(inputFile, with_stemming);
        instances.addThruPipe(it);

        // Create a model with 100 topics, alpha_t = 0.01, beta_w = 0.01
        //  Note that the first parameter is passed as the sum over topics, while
        //  the second is the parameter for a single dimension of the Dirichlet prior.
        //int numTopics = 5;//40
        int numTopics = n_topics;
        ParallelTopicModel model = new ParallelTopicModel(numTopics, 0.01/*1.0*/, 0.01);

        model.addInstances(instances);

        // Use two parallel samplers, which each look at one half the corpus and combine
        //  statistics after every iteration.
        model.setNumThreads(2);
        

        // Run the model for 50 iterations and stop (this is for testing only, 
        //  for real applications, use 1000 to 2000 iterations)
        model.setNumIterations(iter);//1000);
        //System.out.println("Start estimate...");
        model.estimate();
        //System.out.println("End estimate...");

              
        // Show the words and topics in the first instance

        // The data alphabet maps word IDs to strings
        Alphabet dataAlphabet = instances.getDataAlphabet();
        
        //System.out.println(model.getData().get(1).instance.toString());
        
        FeatureSequence tokens = (FeatureSequence) model.getData().get(1).instance.getData();
        LabelSequence topics = model.getData().get(1).topicSequence;
        
        Formatter out = new Formatter(new StringBuilder(), Locale.US);
        for (int position = 0; position < tokens.getLength(); position++) {
            out.format("%s-%d ", dataAlphabet.lookupObject(tokens.getIndexAtPosition(position)), topics.getIndexAtPosition(position));
        }
        //System.out.println(out);
        
        // Estimate the topic distribution of the first instance, 
        //  given the current Gibbs state.
        /*double[] topicDistribution = model.getTopicProbabilities(0);
        
        System.out.println("Topic 0" + Double.valueOf(topicDistribution[0]));
        System.out.println("Topic 1" + Double.valueOf(topicDistribution[1]));
        System.out.println("Topic 2" + Double.valueOf(topicDistribution[2]));
        System.out.println("Topic 3" + Double.valueOf(topicDistribution[3]));
        System.out.println("Topic 4" + Double.valueOf(topicDistribution[4]));
        */
        
        /*Save model topwords on file txt  */
        
        //model.printTopicWordWeights(new File(inputFile.replace(".csv", "_tww.txt")));
        model.printTopWords(new File(inputFile.replace(".csv", "_topwordsModel.txt")), 20, false);
        Reader in = new FileReader(inputFile);
        Writer outcsv = new FileWriter(outputFile);
        Iterable<CSVRecord> records = CSVFormat.newFormat(';').withRecordSeparator("\r\n").withQuoteChar('"').parse(in);
        CSVPrinter printer_csv = new CSVPrinter(outcsv, CSVFormat.newFormat(';').withRecordSeparator("\r\n").withQuoteChar('"'));
        
        int i = -1;
        
        printer_csv.print("PostId");
        //printer_csv.print("Corpus");
        //printer_csv.print("Title");
        //printer_csv.print("Body");
        //printer_csv.print("Tags");
        for(int j = 0; j < n_topics; j++)
        	printer_csv.print("Topic"+j);
        printer_csv.println();
        
        for (CSVRecord record : records) {
    		
        //for(int i=0; i<267; i++){
        if(i != -1){
        	double[] topicDistribution = model.getTopicProbabilities(i);
        	
            printer_csv.print(record.get(0));
            /*if(with_stemming)
            	printer_csv.print(Snowball.extract_stem_corpus(record.get(1)));
            else
            	printer_csv.print(record.get(1));*/
            //printer_csv.print(record.get(2));
            //printer_csv.print(record.get(3));
            for(int j=0; j<model.getNumTopics(); j++)
            	printer_csv.print(topicDistribution[j]);
            
            printer_csv.println();
        }
        	
        //}
        
        i++;
        }
        printer_csv.close();
        
        
        /*Save model on file*/
        
        ObjectOutputStream oos =
                new ObjectOutputStream(new FileOutputStream (modelfile));
            oos.writeObject (model);
            oos.close();
        
        /*Get loglikelihood of trained model*/
            
        double ll= model.modelLogLikelihood();
        
        ObjectOutputStream oos1 =
                new ObjectOutputStream(new FileOutputStream (llfile));
            oos1.writeObject (ll);
            oos1.close();
            
            
            /*save all model info on txt file */
            
            int[] doclengthcount= model.docLengthCounts;   
            int sumlengthcounts=0;
            
            for(int cc=0; cc<doclengthcount.length; cc++)
            {
            	sumlengthcounts= sumlengthcounts + doclengthcount[cc];
            }
            
            int[] tokensPerTopic= model.tokensPerTopic;
            
            int sumlengthtokenspertopic =0;
            for(int cc=0; cc<tokensPerTopic.length; cc++)
            {
            	sumlengthtokenspertopic= sumlengthtokenspertopic + tokensPerTopic[cc];
            }
            
            
            int[][] topicDocCounts = model.topicDocCounts;
            
            int sumtopicdoccounts=0;
            
            for(int cc=0; cc<topicDocCounts.length; cc++)
            {
            	 for(int cc2=0; cc2<topicDocCounts[cc].length; cc2++)
                 {
            		 sumtopicdoccounts= sumtopicdoccounts + topicDocCounts[cc][cc2];
                 }
             }
            
            int totaltokens = model.totalTokens;
            int wordsPerTopic = model.wordsPerTopic;
            
            double lltok = (ll/(double) totaltokens);
            
            //Add info model in new file
                 
            try {
              //File file = new File(llfile);
              File file = new File(llfile.replace(".txt", "infoModel.txt"));
              FileWriter fw = new FileWriter(file);
              
              fw.write("\nLikelihood: "+ Double.toString(ll) +" \n - ");
              fw.write("\nmodel.totalTokens : "+Integer.toString(totaltokens)+" \n - ");
              fw.write("\nmodel.wordsPerTopic : "+Integer.toString(wordsPerTopic)+" \n - ");
              fw.write("\nmodel.docLengthCounts : "+Integer.toString(sumlengthcounts)+" \n - ");
              fw.write("\nmodel.tokensPerTopic : "+Integer.toString(sumlengthtokenspertopic)+" \n - ");
              fw.write("\nmodel.topicDocCounts : "+Integer.toString(sumtopicdoccounts)+" \n - ");
              fw.write("\nLL/tokens : "+Double.toString(lltok)+" \n");
              fw.flush();
              fw.close();
            }
            catch(IOException e) { 
              e.printStackTrace();
            }
        
        
	}
	
	public static void main(String[] args) throws IOException, ClassNotFoundException, InstantiationException, IllegalAccessException {
		// TODO Auto-generated method stub
		if(args.length != 0){
			String input = args[0];
			String output = args[1];
			String stopwords = args[2];
			String modelfile = args[3];
			String llfile = args[4];
			int numTopics = Integer.parseInt(args[5]);
			int iter = Integer.parseInt(args[6]);
			if(args.length == 8){
				if(args[7].equals("--with-stemming"))
					Mallet.topics(input, output, stopwords, modelfile, llfile, numTopics, iter, true);
			}
			else
				Mallet.topics(input, output, stopwords, modelfile, llfile, numTopics, iter, false);
			//String output = input.replace(".csv", "_mallet.csv");
			//Mallet.topics(input, output, stopwords, numTopics, iter);
		}else{
			System.out.println("Usage:\n\tMallet.jar <input_file.csv> <output_file.csv> <stopwords_file.txt> <num_of_topics> <num_of_iterations> [--with-stemming]");
		}
		/************************
		 * Prima di compilare il jar eliminare dal file di output il campo "Corpus", altrimenti consuma troppa memoria
		 */
		
		
		//Mallet.topics("dataset_mallet.csv", "academia_mallet.csv", "lib/mallet-2.0.7/stoplists/en.txt", 40, 500, false);
	}
}

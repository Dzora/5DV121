import java.io.FileNotFoundException;
import java.io.IOException;

public class Faces {
	

	public static void main(String[] args) throws FileNotFoundException, IOException {
		
		if (args.length != 3) {
			System.out.println("Usage: java Faces images.txt keys.txt test.txt");
	    	System.exit(-1);
	    }
		
		Parser parser = new Parser();
		
		Images images = parser.readFile(args[0], args[1]);

		//Trains the happy face
		Trainer happyTrainer = new Trainer(images,1);
		happyTrainer.Learn();

		//Trains the sad face
		Trainer sadTrainer = new Trainer(images,2);
		sadTrainer.Learn();

		//Trains the misschevious face
		Trainer missTrainer = new Trainer(images,3);
		missTrainer.Learn();

		//Trains the happy face
		Trainer angryTrainer = new Trainer(images,4);
		angryTrainer.Learn();
		
		//Trains the mad face
		Parser testParser = new Parser();
		Images testImages = testParser.readFile(args[2], "");

		//Guesses what it is
		Guesser guesser = new Guesser(happyTrainer,sadTrainer,missTrainer,angryTrainer,testImages);
		guesser.guess();
	
	}

}

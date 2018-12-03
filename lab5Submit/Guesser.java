import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Arrays;

public class Guesser {

	private Trainer happyTrainer;
	private Trainer sadTrainer;
	private Trainer missTrainer;
	private Trainer angryTrainer;
	private Images testImages;
	private int[] arr;

	public Guesser(Trainer happy, Trainer sad, Trainer miss, Trainer angry,
			Images testImages) {
		this.happyTrainer = happy;
		this.sadTrainer = sad;
		this.missTrainer = miss;
		this.angryTrainer = angry;
		this.testImages = testImages;

		happyTrainer.perceptron.cleanImages(testImages);
		sadTrainer.perceptron.cleanImages(testImages);
		missTrainer.perceptron.cleanImages(testImages);
		angryTrainer.perceptron.cleanImages(testImages);
	}
	
	/**
	 * Function for guessing what an image is.
	 *
	 * Takes an image from the test set and runs ut through all preceptrons.
	 * The preceptron with the highest value is probably the correct answer.
	 *
	 */
	public void guess() {

			int i = 0;
			arr = new int[testImages.imageBlockMap.size()];

			for (String image : testImages.imageBlockMap.keySet()) {
				addImageToSortingArray(image, i);
				i++;
			}

			sortArray();

			for (int imageNumber : arr) {
				double[][] image = testImages.imageBlockMap.get("Image" + imageNumber);
				
				double a = happyTrainer.perceptron.run(image);

				double b = sadTrainer.perceptron.run(image);

				double c = missTrainer.perceptron.run(image);

				double d = angryTrainer.perceptron.run(image);
			
				double max = Math.max(a, Math.max(b, Math.max(c, d)));

				
				if (max == a) {
						 System.out.println("Image" + imageNumber + " 1");
					} else if (max == b) {
						 System.out.println("Image" + imageNumber + " 2");
					} else if (max == c) {
						 System.out.println("Image" + imageNumber + " 3");
					} else if (max == d) {
						 System.out.println("Image" + imageNumber + " 4");
					}
			}
	}

	/**
	 * A method to add an Image to an array that are used for sorting
	 * @param image
	 * @param i
	 */
	private void addImageToSortingArray(String image, int i) {

		String[] counter = image.split("Image");

		arr[i] = Integer.parseInt(counter[1]);

	}

	/**
	 * A method to sort the array
	 */
	private void sortArray() {
		Arrays.sort(arr);
	}
}

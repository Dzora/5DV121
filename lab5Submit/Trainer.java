import java.lang.reflect.Array;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

public class Trainer {

	public Perceptron perceptron;
	private Images images;
	private int typeOfPerceptron;

	public Trainer(Images images, int typeOfFace) {
		this.images = images;
		this.perceptron = new Perceptron(images);
		this.typeOfPerceptron = typeOfFace;
	}

	/**
	 * The function for training a perceptron.
	 * 1: Suffle the images around for randomness.
	 * 2: Find a correct goal value depending on what image it is training on and what type of perceptron it is.
	 * 3: A small learingRate for slow convergence towards the goal.
	 * 4: Calulate an error.
	 * 5: Update the weigts.
	 * 6: Repeat untill high enough accuracy.
	 *
	 */
	public void Learn() {
		for (int trainingIndex = 0; trainingIndex < 100; trainingIndex++) {
			for (int i = 0; i < images.imageBlockMap.size(); i++) {
				List<String> imageNames = images.imageBlockMap.entrySet().stream().map(e -> e.getKey()).collect(Collectors.toList());

				Collections.shuffle(imageNames);

				double[][] image = images.imageBlockMap.get(imageNames.get(i));

				double activation = perceptron.run(image);
				double goal = 0;

				if (images.facit.get(imageNames.get(i)) == 1
						&& typeOfPerceptron == 1) {
					goal = 1;
				} else if (images.facit.get(imageNames.get(i)) == 2
						&& typeOfPerceptron == 2) {
					goal = 1;
				} else if (images.facit.get(imageNames.get(i)) == 3
						&& typeOfPerceptron == 3) {
					goal = 1;
				} else if (images.facit.get(imageNames.get(i)) == 4
						&& typeOfPerceptron == 4) {
					goal = 1;
				} else {
					goal = 0;
				}

				double learningRate = 0.07;

				double error = goal - activation;

				for (int j = 0; j < perceptron.getPixelVector().size(); j++) {
					double neuron = perceptron.getPixelVector().get(j);

					double deltaW = learningRate * error * neuron;

					perceptron.getWeightVector().set(j,
							perceptron.getWeightVector().get(j) + deltaW);
				}

			}
		}
	}
}

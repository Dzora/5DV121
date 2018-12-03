import java.util.Vector;
import java.util.Random;

public class Perceptron {
	
	private Images images;
	private Vector<Double> pixelVector;
	private Vector<Double> weightVector;
	private boolean doneRandoWeights = false;
	
	public Perceptron(Images images) {
		this.pixelVector = new Vector<>();
		this.weightVector = new Vector<>();
		this.images = images;
	
	
	}

	/**
	 * A method to fill the weight vector with random numbers between 0-1
	 * @param vector
	 */
	private void fillWeightVector(Vector<Double> vector) {
		for (int i = 0; i < pixelVector.size(); i++) {
			Random rand = new Random();
			double random = rand.nextDouble();
			vector.add(random);
		}
		doneRandoWeights = true;
	}

	/**
	 * A method to squash the image into a vector
	 *
	 * @param image
	 */
	private void fillPixelVector(double[][] image) {
		for (int i = 0; i < image.length; i++) {
		    for (int j = 0; j < image[i].length; j++) {
		        pixelVector.add((double)image[i][j]);
		    }
		}
	}

	/**
	 * The run function for a perceptron.
	 *
	 * @param An 20*20 Image that is parsed into the pixelVector
	 * @return	The Activation function result.
	 */
	public double run(double[][] image) {
		pixelVector.clear();

		fillPixelVector(image);
		
		if(!doneRandoWeights) {
			weightVector.clear();
			fillWeightVector(weightVector);
		}	
		
		double d = multiplyVectors();
		
		double sig = sigmoid(d);
	
		return sig;
		
	}

	/**
	 * Multiply one neuron with it's connected weight and sum all of these together.
	 *
	 * @return	The result + added bias.
	 */
	private double multiplyVectors() {
		double res = 0;
		double results = 0;
		double bias = -10;
		
		for(int i = 0; i < pixelVector.size(); i++) {
			
			double d1 = pixelVector.get(i);
			double d2 = weightVector.get(i);
			res = d1 * d2;
			results = res + results;
		
		}
		
		return results + bias;
	}
	
	public void cleanImages(Images images) {
		
		this.images = images;
	}
	
	/**
	 * The Activation function used in this program. (Sigmoid)
	 *
	 * @param The number from multiplyVectors()
	 * @return	The result.
	 */
	private double sigmoid(double x) {
	    return 1 / (1 + Math.exp(-x));
	}

	public Vector<Double> getPixelVector() {
		return pixelVector;
	}

	public void setPixelVector(Vector<Double> pixelVector) {
		this.pixelVector = pixelVector;
	}

	public Vector<Double> getWeightVector() {
		return weightVector;
	}

	public void setWeightVector(Vector<Double> weightVector) {
		this.weightVector = weightVector;
	}
	

}

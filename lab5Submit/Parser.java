import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;

public class Parser {

	private Images images;
	private int matrixIndex = 0;
	private String heading = "";
	private double[][] image;

	public Parser() {
		this.images = new Images();
	}

	/**
	 * A method callable from other classes that read a file.
	 *
	 * @param fileName
	 * @param keyFileName
	 * @return
	 * @throws FileNotFoundException
	 * @throws IOException
	 */
	public Images readFile(String fileName, String keyFileName) throws FileNotFoundException,IOException {
		
		parseImage(fileName);
		if(!keyFileName.isEmpty()) {
			parseFacit(keyFileName);
		}
		return images;
	}

	/**
	 *
	 * @param fileName keys.txt
	 * @throws FileNotFoundException
	 * @throws IOException
	 */
	private void parseFacit(String fileName) throws FileNotFoundException, IOException {
		try (BufferedReader br = new BufferedReader(new FileReader(fileName))) {
			String line;
			while ((line = br.readLine()) != null) {
				
				if(isCommentOrEmpty(line)){
					continue;
				}
				String[] arr = line.split(" ");
				images.facit.put(arr[0], Integer.parseInt(arr[1]));
			}
		}	
	}

	/**
	 *
	 * @param fileName
	 * @throws FileNotFoundException
	 * @throws IOException
	 */
	private void parseImage(String fileName) throws FileNotFoundException, IOException {
		
		try (BufferedReader br = new BufferedReader(new FileReader(fileName))) {
			String line;
			while ((line = br.readLine()) != null) {
				
				if(isCommentOrEmpty(line)){
					continue;
				}
				
				if (matrixIndex == 20) {
					images.imageBlockMap.put(heading, image);
					matrixIndex = 0;
				}
				
				if(checkForImage(line)){
					continue;
				}
				
				buildImage(line);
				
				matrixIndex++;
 			}
			
			images.imageBlockMap.put(heading, image);
		}
	}

	/**
	 * A method to build an image and squash the greyscales into values betweet 0-1
	 * @param line
	 */
	private void buildImage(String line) {
		String[] greyAreas = line.split(" ");
		
		for(int i = 0; i < greyAreas.length; i++) {
			image[matrixIndex][i] = Double.parseDouble(greyAreas[i] ) / 31;
		}
		
	}

	/**
	 * A method to check if a line contains "Image"
	 * @param line
	 * @return
	 */
	private boolean checkForImage(String line) {
		if(line.contains("Image")) {
			heading = line;
			image = new double[20][20];
			return true;
		}
		else {
			return false;
		}
	}

	/**
	 * A method to check if a line is a comment or empty
	 * @param line
	 * @return
	 */
	private boolean isCommentOrEmpty(String line) {
		if(line.isEmpty() || line.contains("#")) {
			return true;
		}
		else {
			return false;
		}
	}

}

package lab5;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;

public class Parser {

	private Images images;
	private int matrixIndex = 0;
	private String heading = "";
	private int[][] image;

	public Parser() {
		this.images = new Images();
	}

	public Images readFile(String fileName) throws FileNotFoundException,IOException {

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
		return images;
	}
	
	private void buildImage(String line) {
		String[] greyAreas = line.split(" ");
		
		for(int i = 0; i < greyAreas.length; i++) {
			image[matrixIndex][i] = Integer.parseInt(greyAreas[i]);
		}
		
	}
	
	private boolean checkForImage(String line) {
		if(line.contains("Image")) {
			heading = line;
			image = new int[20][20];
			return true;
		}
		else {
			return false;
		}
	}
	
	private boolean isCommentOrEmpty(String line) {
		if(line.isEmpty() || line.contains("#")) {
			return true;
		}
		else {
			return false;
		}
	}

}

package lab5;

import java.io.IOException;

public class Main {
	

	public static void main(String[] args) {
		Parser parser = new Parser();
		
		try {
			
			Images images = parser.readFile("images.txt");
			
			int[][] image = images.imageBlockMap.get("Image1");
			
			for (int i = 0; i < image.length; i++) {
			    for (int j = 0; j < image[i].length; j++) {
			        System.out.print(image[i][j] + " ");
			    }
			    System.out.println();
			}
			
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	
	}

}
//package lab5;

import java.io.File;
import java.io.IOException;
import java.util.Scanner;
/*
  Java program that compares two key files for AI assignment 5 HT-18. The percentage of
  lines that match is displayed at the end of the run. Note that the order of the keys
  must be the same for both files.
*/

public class FaceTest
{
   static Scanner resultFile = null;
   static Scanner keyFile = null;

   public static void main(String argv[])
   {
      if (argv.length != 2)
      {
         System.out.println("Usage: java FaceTest resultfile keyfile");
         System.exit(-1);
      }

      // open result and key data files
      try
      {
         resultFile = new Scanner(new File(argv[0]));
         keyFile = new Scanner(new File(argv[1]));
      }
      catch (IOException e)
      {
         e.printStackTrace();
      }


      int ok = 0;
      int images = 0;
      int result;

      // loop through the files and check the network
      do
      {
         result = loadKey(resultFile);
         if (result > 0)
         {
            int facit = loadKey(keyFile);

            if (result == facit) ok++;

            images++;
         }
      } while (result > 0);

      System.out.print("Percentage of correct classifications: " + (100.0 * ok) / images);
      System.out.println("% out of " + images + " images");
   }


   private static int loadKey(Scanner sc)
   {
      if (!sc.hasNext()) return -1;
      
      String token;
      do
         token = sc.next();
      while (sc.hasNext() && !token.startsWith("Image"));

      int out = -1;
      if (sc.hasNextInt())
      {
         out = sc.nextInt();
      }
      return out;
   }

}

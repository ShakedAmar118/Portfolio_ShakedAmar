package image;

import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;

/**
 * A package-private class of the package image.
 * @author Dan Nirel
 */
public class Image {

    private final Color[][] pixelArray;
    private final int width;
    private final int height;

	/**
	 * Constructs an Image from a file.
	 *
	 * @param filename The path to the image file.
	 * @throws IOException If the file cannot be read.
	 */
    public Image(String filename) throws IOException {
        BufferedImage im = ImageIO.read(new File(filename));
        width = im.getWidth();
        height = im.getHeight();


        pixelArray = new Color[height][width];
        for (int i = 0; i < height; i++) {
            for (int j = 0; j < width; j++) {
                pixelArray[i][j]=new Color(im.getRGB(j, i));
            }
        }
    }

	/**
	 * Constructs an Image from a 2D pixel array.
	 *
	 * @param pixelArray A 2D array of Color objects representing pixels.
	 * @param width      The width of the image.
	 * @param height     The height of the image.
	 */
    public Image(Color[][] pixelArray, int width, int height) {
        this.pixelArray = pixelArray;
        this.width = width;
        this.height = height;
    }

	/**
	 * @return The width of the image in pixels.
	 */
    public int getWidth() {
        return width;
    }

	/**
	 * @return The height of the image in pixels.
	 */
    public int getHeight() {
        return height;
    }

	/**
	 * Returns the color of the pixel at a given (x, y) coordinate.
	 *
	 * @param x The row index.
	 * @param y The column index.
	 * @return The Color object representing the pixel at (x, y).
	 */
    public Color getPixel(int x, int y) {
        return pixelArray[x][y];
    }

	/**
	 * Saves the current image to a JPEG file with the given name.
	 * The file is saved with a ".jpeg" extension.
	 *
	 * @param fileName The desired file name (without extension).
	 */
    public void saveImage(String fileName){
        // Initialize BufferedImage, assuming Color[][] is already properly populated.
        BufferedImage bufferedImage = new BufferedImage(pixelArray[0].length, pixelArray.length,
                BufferedImage.TYPE_INT_RGB);
        // Set each pixel of the BufferedImage to the color from the Color[][].
        for (int x = 0; x < pixelArray.length; x++) {
            for (int y = 0; y < pixelArray[x].length; y++) {
                bufferedImage.setRGB(y, x, pixelArray[x][y].getRGB());
            }
        }
        File outputfile = new File(fileName+".jpeg");
        try {
            ImageIO.write(bufferedImage, "jpeg", outputfile);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

}

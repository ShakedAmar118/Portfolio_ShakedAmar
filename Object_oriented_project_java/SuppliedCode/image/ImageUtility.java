package image;

import java.awt.*;

/**
 * A utility class that provides static helper methods for manipulating images,
 * including padding to power-of-two dimensions, splitting into sub-images,
 * and computing normalized brightness values.
 *
 * These operations are used as preprocessing steps before running the ASCII art algorithm.
 *
 * This class is stateless and not intended to be instantiated.
 *
 * @author Shaked Amar
 * @author Hila Gani
 */
public class ImageUtility {
	private static final int BASE_TWO = 2;
	private static final int NUM_OF_PADDINGS = 2;
	private static final double RED_CONSTANT = 0.2126;
	private static final double GREEN_CONSTANT = 0.7152;
	private static final double BLUE_CONSTANT = 0.0722;
	private static final int MAX_RGB_VALUE = 255;

	/**
	 * Pads the given image so that its width and height are both powers of two.
	 * Padding is applied equally on all sides with white pixels.
	 *
	 * @param image The original image to pad.
	 * @return A new Image object with padded dimensions.
	 */
	public static Image padding(Image image) {
		int width = image.getWidth();
		int height = image.getHeight();
		int newWidth = nextPowerOfTwo(width);
		int newHeight = nextPowerOfTwo(height);
		Color[][] newPixelArray = new Color[newHeight][newWidth];
		int paddingWidth = (newWidth - width) / NUM_OF_PADDINGS;
		int paddingHeight = (newHeight - height) / NUM_OF_PADDINGS;

		for (int i = 0; i < newHeight; i++) {
			for (int j = 0; j < newWidth; j++) {
				if (i < paddingHeight || i >= newHeight - paddingHeight ||
						j < paddingWidth || j >= newWidth - paddingWidth) {
					newPixelArray[i][j] = Color.WHITE;
				} else {
					newPixelArray[i][j] = image.getPixel(i - paddingHeight, j - paddingWidth);
				}
			}
		}
		return new Image(newPixelArray, newWidth, newHeight);
	}

	/**
	 * Splits the given image into a grid of square sub-images,
	 * based on the specified resolution.
	 *
	 * @param image      The padded image to split.
	 * @param resolution The number of sub-images per row.
	 * @return A 2D array of Image objects, each representing a square sub-image.
	 */
	public static Image[][] split(Image image, int resolution) {
		int subImageSize = image.getWidth() / resolution;
		Image[][] subImages = new Image[image.getHeight() / subImageSize][resolution];
		for (int i = 0; i < image.getHeight() / subImageSize; i++) {
			for (int j = 0; j < resolution; j++) {

				Color[][] subImagePixels = new Color[subImageSize][subImageSize];
				for (int x = 0; x < subImageSize; x++) {
					for (int y = 0; y < subImageSize; y++) {
						subImagePixels[x][y] = image.getPixel(i * subImageSize + x, j * subImageSize + y);
					}
				}
				subImages[i][j] = new Image(subImagePixels, subImageSize, subImageSize);

			}
		}
		return subImages;
	}

	/**
	 * Calculates the normalized brightness of an image based on the weighted
	 * contribution of its red, green, and blue components.
	 *
	 * The result is a value between 0 and 1.
	 *
	 * @param image The image to analyze.
	 * @return The normalized brightness of the image.
	 */
	public static double brightness(Image image) {
		double sumBrightness = 0;
		int numOfPixels = image.getWidth() * image.getHeight();
		for (int i = 0; i < image.getHeight(); i++) {
			for (int j = 0; j < image.getWidth(); j++) {
				Color color = image.getPixel(i, j);
				sumBrightness += color.getRed() * RED_CONSTANT +
						color.getGreen() * GREEN_CONSTANT + color.getBlue() * BLUE_CONSTANT;
			}
		}
		return (sumBrightness / numOfPixels) / MAX_RGB_VALUE;
	}

	/**
	 * @param image The original image.
	 * @return The width of the image after padding to the next power of two.
	 */
	public static int getWidthAfterPadding(Image image) {
		return nextPowerOfTwo(image.getWidth());
	}

	/**
	 * @param image The original image.
	 * @return The height of the image after padding to the next power of two.
	 */
	public static int getHeightAfterPadding(Image image) {
		return nextPowerOfTwo(image.getHeight());
	}

	/**
	 * Computes the smallest power of two greater than or equal to the given number.
	 *
	 * @param n The number to round up.
	 * @return The next power of two.
	 */
	private static int nextPowerOfTwo(int n) {
		if ((n & (n - 1)) == 0){
			return n;
		}
		int power = 1;
		while (power < n) {
			power *= BASE_TWO;
		}
		return power;
	}

}

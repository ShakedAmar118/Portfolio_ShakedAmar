package image;

/**
 * Manages the brightness values of sub-images derived from a padded version
 * of the input image. Handles both the image padding and the brightness computation.
 *
 * This class caches the brightness values to avoid recomputation unless
 * the resolution is explicitly changed.
 *
 * Used as a preprocessing step before running the ASCII art algorithm.
 *
 * @author Shaked Amar
 * @author Hila Gani
 */
public class SubImgBrightnesses {

	private int resolution;
	private Image paddedImage;
	private double[][] brightnesses;

	/**
	 * Constructs a new SubImgBrightnesses object by padding the original image
	 * and storing the resolution to be used for splitting it into sub-images.
	 *
	 * @param image      The original image to be padded and processed.
	 * @param resolution The number of sub-images per row.
	 */
	public SubImgBrightnesses(Image image, int resolution) {
		paddedImage = ImageUtility.padding(image);
		brightnesses = null;
		this.resolution = resolution;
	}

	/**
	 * Recalculates and stores the brightness values for the current resolution
	 * by splitting the padded image into sub-images and computing the brightness
	 * of each one.
	 *
	 * @param resolution The new resolution to apply when splitting the image.
	 * @return A 2D array of normalized brightness values.
	 */
	public double[][] createBrightnesses(int resolution) {
		this.resolution = resolution;
		Image[][] subImages = ImageUtility.split(paddedImage, resolution);
		brightnesses = new double[subImages.length][subImages[0].length];
		for (int i = 0; i < subImages.length; i++) {
			for (int j = 0; j < subImages[i].length; j++) {
				brightnesses[i][j] = ImageUtility.brightness(subImages[i][j]);
			}
		}
		return brightnesses;
	}

	/**
	 * Returns the cached brightness matrix if it exists, or computes it if needed.
	 *
	 * @return A 2D array of normalized brightness values for all sub-images.
	 */
	public double[][] getBrightnesses() {
		if (brightnesses == null) {
			return createBrightnesses(resolution);
		}
		return brightnesses;
	}
}

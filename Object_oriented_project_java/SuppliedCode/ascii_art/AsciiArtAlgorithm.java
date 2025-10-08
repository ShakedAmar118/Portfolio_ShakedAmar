package ascii_art;

import image.Image;
import image.ImageUtility;
import image_char_matching.Round;
import image_char_matching.SubImgCharMatcher;

/**
 * Implements the core ASCII art algorithm that converts brightness values
 * of sub-images into ASCII characters using a matching strategy.
 *
 * @author Shaked Amar
 * @author Hila Gani
 */
public class AsciiArtAlgorithm {

	private double[][] subImgBrightnesses;
	private final SubImgCharMatcher charMatcher;

	/**
	 * Constructs a new AsciiArtAlgorithm instance.
	 *
	 * @param round                The rounding method to apply (ABS, UP, DOWN).
	 * @param charMatcher          The character matcher used to select characters by brightness.
	 * @param subImgBrightnesses   A 2D array of normalized brightness values, one per sub-image.
	 */
	public AsciiArtAlgorithm(Round round, SubImgCharMatcher charMatcher, double[][] subImgBrightnesses) {
		this.subImgBrightnesses = subImgBrightnesses;
		this.charMatcher = charMatcher;
		charMatcher.setRound(round);
	}

	/**
	 * Runs the ASCII art conversion algorithm.
	 *
	 * @return A 2D array of characters representing the final ASCII art image.
	 */
	public char[][] run(){
		char[][] asciiArt = new char[subImgBrightnesses.length][subImgBrightnesses[0].length];
		for (int i = 0; i < subImgBrightnesses.length; i++) {
			for (int j = 0; j < subImgBrightnesses[i].length; j++) {
				asciiArt[i][j] = charMatcher.getCharByImageBrightness(subImgBrightnesses[i][j]);
			}
		}
		return asciiArt;
	}
}

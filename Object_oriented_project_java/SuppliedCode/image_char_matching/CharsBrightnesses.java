package image_char_matching;

import static image_char_matching.CharConverter.DEFAULT_PIXEL_RESOLUTION;
import java.util.HashMap;

/**
 * A singleton class responsible for computing and caching the raw brightness
 * of each ASCII character based on its 2D boolean pixel matrix representation.
 *
 * Brightness is computed only once per character and stored for reuse across
 * multiple ASCII art conversions. This improves performance by avoiding redundant calculations.
 *
 * The class uses the CharConverter to obtain pixel matrices and computes brightness
 * as the ratio of 'on' pixels out of the total number of pixels.
 *
 * @author Shaked Amar
 * @author Hila Gani
 */
public class CharsBrightnesses {

	private static CharsBrightnesses singletonCharsBrightnesses;
	private final HashMap<Character, Double> charsBrightnessesMap;

	/**
	 * Private constructor for singleton pattern.
	 */
	private CharsBrightnesses() {
		charsBrightnessesMap = new HashMap<>();
	}

	/**
	 * Returns the singleton instance of CharsBrightnesses.
	 *
	 * @return The single global instance.
	 */
	public static CharsBrightnesses getInstance() {
		if (singletonCharsBrightnesses == null) {
			singletonCharsBrightnesses = new CharsBrightnesses();
		}
		return singletonCharsBrightnesses;
	}

	/**
	 * Computes and stores the brightness of a character if it hasn't been calculated yet.
	 * Brightness is calculated as the ratio of 'true' pixels to total pixels in the
	 * character's 2D boolean matrix.
	 *
	 * @param c The character whose brightness should be computed.
	 */
	public void addCharBrightness(char c) {
		if (charsBrightnessesMap.containsKey(c)) {
			return;
		}
		boolean[][] charBoolMatrix = CharConverter.convertToBoolArray(c);
		int trueCounter = 0;
		for (int i = 0; i < DEFAULT_PIXEL_RESOLUTION; i++) {
			for (int j = 0; j < DEFAULT_PIXEL_RESOLUTION; j++) {
				if(charBoolMatrix[i][j]) {
					trueCounter++;
				}
			}
		}
		double charBrightness = (double)trueCounter / (DEFAULT_PIXEL_RESOLUTION * DEFAULT_PIXEL_RESOLUTION);
		charsBrightnessesMap.put(c, charBrightness);
	}

	/**
	 * Returns the cached brightness value of the given character.
	 * If the character was not previously added, returns -1.0.
	 *
	 * @param c The character to query.
	 * @return The brightness of the character, or -1.0 if not found.
	 */
	public double getCharBrightness(char c) {
		if (charsBrightnessesMap.containsKey(c)) {
			return charsBrightnessesMap.get(c);
		}
		return -1.0;
	}
}

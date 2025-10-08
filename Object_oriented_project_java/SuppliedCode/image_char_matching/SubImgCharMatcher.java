package image_char_matching;

import java.util.TreeMap;
import java.util.TreeSet;

/**
 * Matches normalized brightness values of sub-images to ASCII characters
 * based on a given character set and rounding mode.
 *
 * Internally maintains a mapping from normalized brightness values
 * to characters, and updates the mapping when characters are added or removed.
 * Uses a combination of raw and normalized brightness tracking for efficiency.
 *
 * This class supports three rounding modes (ABS, UP, DOWN) to determine
 * the closest matching character for a given brightness.
 *
 * @author Shaked Amar
 * @author Hila Gani
 */
public class SubImgCharMatcher {

	private static final String SPACE_STR = " ";

	private final TreeSet<Character> charSet;
	private TreeMap<Double, TreeSet<Character>> normalBrightnessMap;
	private final CharsBrightnesses charsBrightnesses;
	private Round round = Round.ABS;
	private double maxBrightness;
	private double minBrightness;
	private boolean setBrightnesses;

	/**
	 * Constructs a matcher initialized with a given character set.
	 * Computes brightness values and prepares internal mappings.
	 *
	 * @param charset The array of characters to initialize the matcher with.
	 */
	public SubImgCharMatcher(char[] charset) {
		charSet = new TreeSet<>();
		normalBrightnessMap = new TreeMap<>();
		charsBrightnesses = CharsBrightnesses.getInstance();
		maxBrightness = 0.0;
		minBrightness = 1.0;
		setBrightnesses = true;
		for (char c : charset) {
			addChar(c);
		}
	}

	/**
	 * Returns the character from the current charset whose brightness
	 * best matches the given brightness value, according to the selected rounding mode.
	 *
	 * @param brightness The normalized brightness value (between 0 and 1).
	 * @return The matching ASCII character.
	 */
	public char getCharByImageBrightness(double brightness) {
		if(setBrightnesses){
			updateBrightnesses();
			setBrightnesses = false;
		}
		if(brightness >= normalBrightnessMap.lastKey()){
			return normalBrightnessMap.get(normalBrightnessMap.lastKey()).first();
		}
		if(brightness <= normalBrightnessMap.firstKey()){
			return normalBrightnessMap.get(normalBrightnessMap.firstKey()).first();
		}
		double closestUpperBrightness = normalBrightnessMap.ceilingKey(brightness);
		double closestLowerBrightness = normalBrightnessMap.floorKey(brightness);
		if(round == Round.UP) {
			return normalBrightnessMap.get(closestUpperBrightness).first();
		}
		if(round == Round.DOWN) {
			return normalBrightnessMap.get(closestLowerBrightness).first();
		}

		// round == Round.ABS
		if (closestUpperBrightness - brightness < brightness - closestLowerBrightness) {
			return normalBrightnessMap.get(closestUpperBrightness).first();
		} else {
			return normalBrightnessMap.get(closestLowerBrightness).first();
		}
	}

	/**
	 * Adds a character to the matcher and updates brightness mappings.
	 *
	 * @param c The character to add.
	 */
	public void addChar(char c) {
		boolean isMaxOrMinChanged = false;
		charSet.add(c);
		charsBrightnesses.addCharBrightness(c);
		double cBrightness = charsBrightnesses.getCharBrightness(c);

		if(cBrightness > maxBrightness){
			maxBrightness = cBrightness;
			setBrightnesses = true;
			isMaxOrMinChanged = true;
		}
		if(cBrightness < minBrightness){
			minBrightness = cBrightness;
			setBrightnesses = true;
			isMaxOrMinChanged = true;
		}
		if(!isMaxOrMinChanged){
			addCharToNormalBrightnessMap(c);
		}
	}

	/**
	 * Removes a character from the matcher and updates brightness mappings
	 * if necessary.
	 *
	 * @param c The character to remove.
	 */
	public void removeChar(char c) {
		charSet.remove(c);

		double cBrightness = charsBrightnesses.getCharBrightness(c);
		if (cBrightness == maxBrightness || cBrightness == minBrightness) {
			setBrightnesses = true;
			updateMaxMinBrightness();
			return;
		}

		double cNormalBrightness = getCharNormalBrightness(c);
		if (normalBrightnessMap.containsKey(cNormalBrightness)) {
			normalBrightnessMap.get(cNormalBrightness).remove(c);
			if (normalBrightnessMap.get(cNormalBrightness).isEmpty()) {
				normalBrightnessMap.remove(cNormalBrightness);
			}
		}
	}

	/**
	 * Updates the rounding mode used for matching characters.
	 *
	 * @param round The rounding mode to set (ABS, UP, DOWN).
	 */
	public void setRound(Round round) {
		this.round = round;
	}


	/**
	 * @return The number of characters currently in the matcher.
	 */
	public int getCharsetSize() {
		return charSet.size();
	}

	/**
	 * Returns the character set as a sorted space-separated string,
	 * used for the 'chars' command output.
	 *
	 * @return A string representation of the current charset.
	 */
	@Override
	public String toString() {
		StringBuilder result = new StringBuilder();
		for (char c : charSet) {
			result.append(c).append(SPACE_STR);
		}
		return result.toString();
	}

	/**
	 * Recalculates the maximum and minimum raw brightness values
	 * across all characters currently in the charset.
	 * This method is called when a character with min or max brightness
	 * is removed, in order to reestablish correct normalization bounds.
	 */
	private void updateMaxMinBrightness(){
		for(char c : charSet){
			double cBrightness = charsBrightnesses.getCharBrightness(c);
			if(cBrightness > maxBrightness){
				maxBrightness = cBrightness;
			}
			if(cBrightness < minBrightness){
				minBrightness = cBrightness;
			}
		}
	}

	/**
	 * Computes the normalized brightness of a given character,
	 * based on current min and max brightness in the charset.
	 *
	 * @param c The character whose normalized brightness is to be calculated.
	 * @return The normalized brightness value (between 0 and 1).
	 */
	private double getCharNormalBrightness(char c) {
		double cBrightness = charsBrightnesses.getCharBrightness(c);
		return (cBrightness - minBrightness) / (maxBrightness - minBrightness);
	}

	/**
	 * Rebuilds the entire mapping of normalized brightness values
	 * to characters, based on the current charset.
	 *
	 * This method is called when min or max brightness changes,
	 * requiring a full re-normalization of the brightness map.
	 */
	private void updateBrightnesses() {
		normalBrightnessMap = new TreeMap<>();
		for(char c : charSet){
			addCharToNormalBrightnessMap(c);
		}
	}

	/**
	 * Adds a character to the normalized brightness map.
	 * If other characters share the same normalized brightness,
	 * they are grouped together in a sorted set.
	 *
	 * @param c The character to add.
	 */
	private void addCharToNormalBrightnessMap(char c) {
		double cNormalBrightness = getCharNormalBrightness(c);
		if (normalBrightnessMap.containsKey(cNormalBrightness)) {
			normalBrightnessMap.get(cNormalBrightness).add(c);
		} else {
			TreeSet<Character> newSet = new TreeSet<>();
			newSet.add(c);
			normalBrightnessMap.put(cNormalBrightness, newSet);
		}
	}
}

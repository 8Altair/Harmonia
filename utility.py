import librosa as rosa, numpy as np

from librosa.feature import rms
from librosa.util import valid_audio

from logging_configuration import  preprocessing_logger, language_decision_logger


SAMPLING_RATE = 16000   # Sampling frequency preffered for NLP pipeline

def standardize_audio(audio_input: str | np.ndarray, sampling_rate: int = SAMPLING_RATE) -> np.ndarray:
    """
        Standardize audio input for NLP pipeline processing.

        This function:
        - loads audio files
        - converts multichannel audio to mono
        - converts audio to float32
        - resamples audio to the configured sampling rate
        - validates audio integrity

        Parameters
        ----------
        audio_input : str | np.ndarray
            Audio file path or NumPy audio array.

        sampling_rate : int, optional
            Original sampling rate of NumPy audio input.
            Defaults to the configured NLP pipeline sampling rate.

        Returns
        -------
        np.ndarray
            Standardized mono float32 audio array.

        Raises
        ------
        FileNotFoundError
            If the provided audio file does not exist.

        TypeError
            If the audio input type is unsupported.

        Exception
            If audio loading, conversion, resampling, or validation fails.
    """
    preprocessing_logger.debug("Standardizing audio.")
    if isinstance(audio_input, str):
        preprocessing_logger.debug("Audio input is a string.")
        try:
            audio = rosa.load(audio_input, sr=SAMPLING_RATE, mono=True)[0]
            preprocessing_logger.debug(f"Audio file {audio_input} loaded.")
        except FileNotFoundError:
            preprocessing_logger.exception("Audio not found.")
            raise
        except Exception:
            preprocessing_logger.exception("There was a problem with audio loading.")
            raise
    elif isinstance(audio_input, np.ndarray):
        preprocessing_logger.debug("Audio input is a NumPy array.")

        try:
            audio = np.asarray(audio_input, dtype=np.float32)
            preprocessing_logger.debug("Converted array into explicit np.float32 type.")

            if audio.ndim > 1:  # Check if the number of audio channels is non-mono
                preprocessing_logger.debug("Audio is multichannel. Converting to mono.")
                audio = rosa.to_mono(audio)

            if sampling_rate != SAMPLING_RATE:
                preprocessing_logger.debug(f"Resampling audio from {sampling_rate} Hz to {SAMPLING_RATE} Hz.")
                audio = rosa.resample(audio, orig_sr=sampling_rate, target_sr=SAMPLING_RATE)

        except Exception:
            preprocessing_logger.exception("There was a problem with audio array conversion.")
            raise
    else:
        preprocessing_logger.error("Audio input is not a string or a NumPy array.")
        raise TypeError("Audio input must be a file path or NumPy array.")

    try:
        valid_audio(audio)
        preprocessing_logger.debug("Audio validation successful.")
    except Exception:
        preprocessing_logger.exception("Audio is not valid.")
        raise

    preprocessing_logger.debug("Returning standardized audio.")
    return audio


def is_empty_audio(audio: np.ndarray) -> bool:
    """
        Check whether an audio array is empty.

        Parameters
        ----------
        audio : np.ndarray
            Audio array to validate.

        Returns
        -------
        bool
            True if the audio array is empty, otherwise False.
    """
    preprocessing_logger.debug("Checking if an audio is empty.")
    return audio.size == 0


def duration_validation(audio: np.ndarray) -> bool:
    """
        Validate that audio duration is at least 300 milliseconds.

        Parameters
        ----------
        audio : np.ndarray
            Standardized audio array.

        Returns
        -------
        bool
            True if audio duration is at least 300 ms, otherwise False.

        Raises
        ------
        Exception
            If audio duration calculation fails.
    """
    preprocessing_logger.debug("Checking whether audio duration is at least 300 ms.")
    try:
        duration = rosa.get_duration(y=audio, sr=SAMPLING_RATE)
    except Exception:
        preprocessing_logger.exception("There was a problem with audio duration checking.")
        raise

    preprocessing_logger.info(f"Audio duration is {duration} s.")
    return duration >= 0.3


def silence_validation(audio: np.ndarray) -> bool:
    """
        Validate that audio energy exceeds the silence threshold.

        The validation is based on the mean root mean square (RMS)
        energy level of the audio signal.

        Parameters
        ----------
        audio : np.ndarray
            Standardized audio array.

        Returns
        -------
        bool
            True if the audio energy exceeds the silence threshold,
            otherwise False.

        Raises
        ------
        Exception
            If RMS or mean RMS calculation fails.
    """
    preprocessing_logger.debug("Calculating root mean square for energy level comparison.")
    try:
        root_mean_square = rms(y=audio)
    except Exception:
        preprocessing_logger.exception("Could not calculate root mean square.")
        raise
    preprocessing_logger.debug("Calculating the mean of all root mean square elements.")
    try:
        mean_rms = float(np.mean(root_mean_square)) # Mean explicitely converted to float for uniform type usage
    except Exception:
        preprocessing_logger.exception("Could not calculate mean of root mean square.")
        raise

    preprocessing_logger.info(f"Mean of RMS is {mean_rms}.")
    return mean_rms > 0.001


def decider(probabilities: dict[str, float]) -> str | tuple[str, bool] | tuple[str, str, bool] | tuple[
    str, str, str, bool]:
    language_decision_logger.debug("Starting language decision process.")
    sorted_probabilities = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)  # Sort language probability dictionary as items using a value as a sorting key for descending order
    n = 3
    top_n = sorted_probabilities[:n] if len(sorted_probabilities) > n else sorted_probabilities  # Take top n (3 or 2) probability items
    language_decision_logger.debug(f"Top {n} languages are: {top_n}.")
    probabilities_size = len(top_n)  # Define the size of the top n list

    first_item = top_n[0]  # Take the highest probability item from the top n
    if probabilities_size == 1:  # Logic only for a single language probability detected
        detected_language = first_item[0]  # Store the language from the highest probability item
        language_decision_logger.debug(f"There is only one language detected: {detected_language}.")
    else:  # Logic for a multiple language probability detected
        high_certainty = 0.85  # Custom threshold for a high confidence level
        medium_certainty = 0.7  # Custom threshold for a medium confidence level
        low_certainty = 0.55  # Custom threshold for a low confidence level

        if first_item[1] > high_certainty:  # Logic for the highest probability above the high_certainty treshold; model is verys condfident that this is the best language candidate
            detected_language = first_item[0]
        else:  # Other cases
            language_decision_logger.debug("Multiple languages detected.")

            epsilon_low = 0.03  # Epsilon surrounding for the higher probabilities: higher probabilties are more meaningful and more likely to show if the highest probability is around the high_certainty
            epsilon_medium = 0.05  # Epsilon surrounding for the medium probabilities: medium probabilties are still good, but less meaningful, and are a little bit harder to find if the highest probability is around the medium_certainty
            epsilon_high = 0.1  # Epsilon surrounding for the lower probabilities: low probabilities are less meaningful, and are likely harder to find if the highest probability is around the low_certainty

            detected_language = [first_item[0]]  # First language is always returned
            category = 1  # Medium category
            second_item = top_n[1]  # Take the second-highest probability item from the top n
            first_second_difference = first_item[1] - second_item[1]  # Calculate the difference between the first and the second probability

            # Take the second language if possible
            if medium_certainty < first_item[1] <= high_certainty:  # Medium category
                if first_second_difference <= epsilon_low:  # The second-highest probability falls into an epsilon surrounding
                    detected_language.append(second_item[0])  # Probabilities are high enough to be considered trustworthy
            elif low_certainty < first_item[1] <= medium_certainty:  # Low category
                category = 2  # Low category
                if first_second_difference <= epsilon_medium:
                    detected_language.append(second_item[0])
            elif first_item[1] <= low_certainty:  # Critical category
                category = 3  # Critical category
                if first_second_difference <= epsilon_high:
                    detected_language.append(second_item[0])
                    detected_language.append(False)  # Probabilities are not high enough to be considered trustworthy

            if len(detected_language) == 1:  # Only the first element can be appended because of the epsilon rule
                detected_language = [first_item[0], False] if first_item[1] <= low_certainty else [first_item[0], True]  # Store the highest probability language, and the bool value meaning the detection is confident or not confident enough that this could be the language processed

            # Logic for the top 3
            if probabilities_size == 3 and len(detected_language) == n - 1:  # There must be exactly 3 languages available and the current list must have 2 languages confidently
                third_item = top_n[2]  # Take the language from the third-highest probability item
                first_third_difference = first_item[1] - third_item[1]  # Calculate the difference between the first and the third probability
                if category == 1 and first_third_difference <= epsilon_low:
                    detected_language.append(third_item[0])
                elif category == 2 and first_third_difference <= epsilon_medium:
                    detected_language.append(third_item[0])
                elif category == 3 and first_third_difference <= epsilon_high:
                    detected_language.append(third_item[0])
                    detected_language.append(False)

            if not isinstance(detected_language[-1], bool) and (len(detected_language) == 2 or len(detected_language) == 3):  # If the second and/or third language is added and the certainty is high
                detected_language.append(True)
            detected_language = tuple(detected_language)

    language_decision_logger.debug(f"Returning {len(detected_language) - 1} language(s): {detected_language}.")
    return detected_language

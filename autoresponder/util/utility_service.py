import ast
import logging
import re
from typing import Optional

# utility_service.py or in utils.py within your app directory
logger = logging.getLogger(__name__)


class UtilityService:

    @staticmethod
    def decode_byte_string(byte_string: str) -> Optional[str]:
        """
        This method takes a byte string and decodes it to a normal string.
        It assumes the byte string is encoded with UTF-8.
        If decoding fails, it returns None or raises an exception based on the flag.

        :param byte_string: The byte string to decode.
        :type byte_string: bytes
        :return: The decoded string.
        :rtype: str or None
        """
        try:
            # Assuming the byte string is encoded with UTF-8.
            # You can change the encoding if you know the byte string uses a different one.
            byte_string = ast.literal_eval(byte_string)
            return byte_string.decode('utf-8').strip()
        except UnicodeDecodeError as e:
            # You can handle the exception as needed
            logger.error(f"Error decoding byte string: {e}")
            return None  # or you could re-raise the exception after logging

    @staticmethod
    def extract_text_before_first_case_number(text: str) -> str:
        """
        Extrahiert den Text vor dem ersten Aktenzeichen im übergebenen Text.

        :param text: Der zu durchsuchende Text.
        :return: Der Text vor dem ersten Aktenzeichen oder ein leerer String, falls kein Aktenzeichen gefunden wurde.
        """
        # Diese Regex sucht nach 'Az.' gefolgt von einer optionalen Leerzeichen-Menge,
        # dann einer Gruppe von Zahlen, Buchstaben und Zeichen, die typisch für Aktenzeichen sind.
        match = re.search(r"^(.*?)(?=\s*Az\.\s*\d+\s*[A-Za-z]+\s*\d+/\d+)", text, re.DOTALL)

        if match:
            return match.group(1).strip()

        return ""  # Gib einen leeren String zurück, wenn kein Aktenzeichen gefunden wurde.

    @staticmethod
    def cut_string_to_length(input_string, max_length=14000):
        """
        Kürzt einen String auf eine maximale Länge von 14000 Zeichen.

        :param input_string: Der zu kürzende String.
        :param max_length: Die maximale Länge des Strings (Standardwert ist 14000).
        :return: Der gekürzte String.
        """
        if len(input_string) > max_length:
            return input_string[:max_length]
        return input_string

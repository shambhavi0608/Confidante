"""
Translator Module - English to Hindi and other language translations.

This module uses Google Translate to convert text to different languages
with caching to minimize API calls.
"""

import os


class Translator:
    """
    Translates text to different languages using Google Translate.
    
    Supports multiple languages with caching to optimize API usage.
    """
    
    def __init__(self):
        """
        Initialize the Translator.
        
        Example:
            translator = Translator()
            hindi_text = translator.translate_to_hindi("Hello")
        """
        try:
            from googletrans import Translator as GoogleTranslator
            self.translator = GoogleTranslator()
            self.translator_available = True
        except Exception as e:
            print(f"⚠ Warning: Google Translate not available: {e}")
            self.translator = None
            self.translator_available = False
        
        # Cache translations to reduce API calls
        self.cache = {}

    def translate_to_hindi(self, text):
        """
        Translate English text to Hindi.
        
        Args:
            text (str): English text to translate
            
        Returns:
            str: Hindi translation or original text if translation fails
            
        Example:
            hindi = translator.translate_to_hindi("Hello world")
            print(hindi)  # "नमस्ते दुनिया"
        """
        return self.translate_to_language(text, 'hi')

    def translate_to_language(self, text, lang_code):
        """
        Translate text to specified language.
        
        Args:
            text (str): Text to translate
            lang_code (str): Language code (e.g., 'hi', 'es', 'fr')
            
        Returns:
            str: Translated text or original if translation fails
            
        Example:
            spanish = translator.translate_to_language("Hello", 'es')
            print(spanish)  # "Hola"
        """
        if not text or text.strip() == "":
            return ""
        
        # Create cache key
        cache_key = f"{text}_{lang_code}"
        
        # Check cache first
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        if not self.translator_available or self.translator is None:
            self.cache[cache_key] = text
            return text
        
        try:
            # Translate using Google Translate
            result = self.translator.translate(text, src_language='en', dest_language=lang_code)
            translated = result.get('text', text)
            
            # Store in cache
            self.cache[cache_key] = translated
            
            return translated
            
        except Exception as e:
            print(f"Translation error: {e}")
            # Return original text as fallback
            self.cache[cache_key] = text
            return text

    def get_language_options(self):
        """
        Get available language options.
        
        Returns:
            dict: Language names mapped to language codes
            
        Example:
            langs = translator.get_language_options()
            print(langs)  # {'Hindi': 'hi', 'Spanish': 'es', ...}
        """
        return {
            'Hindi': 'hi',
            'Spanish': 'es',
            'French': 'fr',
            'German': 'de',
            'Chinese (Simplified)': 'zh-cn',
            'Japanese': 'ja',
            'Korean': 'ko',
            'Portuguese': 'pt',
            'Arabic': 'ar',
            'Russian': 'ru'
        }

    def clear_cache(self):
        """
        Clear the translation cache.
        
        Example:
            translator.clear_cache()
            print(len(translator.cache))  # 0
        """
        self.cache.clear()

    def get_cache_info(self):
        """
        Get information about cached translations.
        
        Returns:
            dict: Cache statistics
            
        Example:
            info = translator.get_cache_info()
            print(f"Cached translations: {info['total']}")
        """
        return {
            'total_cached': len(self.cache),
            'language_codes': list(set([k.split('_')[-1] for k in self.cache.keys()]))
        }

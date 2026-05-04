"""
Sentence Builder Module - Converts detected gestures into words and sentences.

This module manages the logic for converting individual letters (from gesture detection)
into complete words and sentences with intelligent cooldown and confirmation logic.
"""


class SentenceBuilder:
    """
    Builds sentences from detected sign language gestures.
    
    Converts individual letters into words with cooldown logic to prevent
    duplicate captures and provides sentence management functionality.
    """
    
    def __init__(self):
        """
        Initialize the SentenceBuilder.
        
        Example:
            builder = SentenceBuilder()
            builder.add_letter('H', 0.9)
            builder.add_letter('E', 0.85)
            print(builder.get_full_sentence())  # "HE"
        """
        self.current_letters = []           # Individual letters being typed
        self.current_word = ""              # Word being formed from letters
        self.sentence_words = []            # Complete words in the sentence
        self.last_letter = None             # Previous letter (to detect repeats)
        self.letter_cooldown = 0            # Frames since last letter added
        self.COOLDOWN_FRAMES = 20           # Wait 20 frames between letters (prevents duplicates)
        self.confirmation_buffer = []       # Hold gesture for confirmation

    def add_letter(self, letter, confidence):
        """
        Add a detected letter to the current word.
        
        Args:
            letter (str): Gesture label (single letter, digit, or control command)
            confidence (float): Detection confidence (0-1)
            
        Returns:
            dict: Current state with letters, words, and sentence
            
        Example:
            state = builder.add_letter('A', 0.9)
            state = builder.add_letter('B', 0.85)
            print(state['current_word'])  # "AB"
        """
        # Ignore NOTHING gesture
        if letter == 'NOTHING':
            self.letter_cooldown += 1
            return self.get_display_info()
        
        # Handle SPACE: complete current word and add to sentence
        if letter == 'SPACE':
            if self.current_word:
                self.sentence_words.append(self.current_word)
                self.current_word = ""
                self.current_letters = []
            self.letter_cooldown = 0
            self.last_letter = None
            return self.get_display_info()
        
        # Handle CLEAR: reset everything
        if letter == 'CLEAR':
            self.current_word = ""
            self.current_letters = []
            self.sentence_words = []
            self.letter_cooldown = 0
            self.last_letter = None
            self.confirmation_buffer = []
            return self.get_display_info()
        
        # Apply cooldown: only add letter if enough frames have passed
        if self.letter_cooldown > 0 and self.letter_cooldown < self.COOLDOWN_FRAMES:
            self.letter_cooldown += 1
            return self.get_display_info()
        
        # Increase cooldown requirement if same letter as last (avoid rapid repeats)
        if letter == self.last_letter:
            # Require double the cooldown for same letter
            required_cooldown = self.COOLDOWN_FRAMES * 2
            if self.letter_cooldown < required_cooldown:
                self.letter_cooldown += 1
                return self.get_display_info()
        
        # Add letter to current word
        if self.letter_cooldown == 0 or self.letter_cooldown >= self.COOLDOWN_FRAMES:
            self.current_word += letter
            self.current_letters.append(letter)
            self.last_letter = letter
            self.letter_cooldown = 1  # Start new cooldown
        
        return self.get_display_info()

    def get_current_word(self):
        """
        Get the currently formed word.
        
        Returns:
            str: Current word being typed
            
        Example:
            builder.add_letter('C', 0.9)
            builder.add_letter('A', 0.85)
            builder.add_letter('T', 0.88)
            print(builder.get_current_word())  # "CAT"
        """
        return self.current_word

    def get_full_sentence(self):
        """
        Get the complete sentence including words and current partial word.
        
        Returns:
            str: Full sentence with spaces between complete words
            
        Example:
            builder.sentence_words = ['HELLO', 'WORLD']
            builder.current_word = 'THIS'
            print(builder.get_full_sentence())  # "HELLO WORLD THIS"
        """
        words = self.sentence_words + ([self.current_word] if self.current_word else [])
        return ' '.join(words)

    def complete_sentence(self):
        """
        Finalize the current sentence and reset all buffers.
        
        Returns:
            str: Complete sentence
            
        Example:
            builder.add_letter('H', 0.9)
            builder.add_letter('I', 0.85)
            sentence = builder.complete_sentence()
            print(sentence)  # "HI"
            print(builder.get_full_sentence())  # "" (reset)
        """
        # Add current word to sentence words if it exists
        if self.current_word:
            self.sentence_words.append(self.current_word)
        
        # Get complete sentence
        complete_sentence = ' '.join(self.sentence_words)
        
        # Reset all buffers
        self.current_word = ""
        self.current_letters = []
        self.sentence_words = []
        self.last_letter = None
        self.letter_cooldown = 0
        self.confirmation_buffer = []
        
        return complete_sentence

    def get_display_info(self):
        """
        Get all display information in one dictionary.
        
        Returns:
            dict: Display information with keys:
                - 'current_letter': Last added letter
                - 'current_word': Currently formed word
                - 'sentence': Full sentence
                - 'word_count': Number of complete words
                - 'letter_count': Total letters typed
                
        Example:
            info = builder.get_display_info()
            print(info['sentence'])  # "HELLO WORLD HI"
            print(info['word_count'])  # 3
        """
        return {
            'current_letter': self.last_letter if self.last_letter else '—',
            'current_word': self.current_word,
            'sentence': self.get_full_sentence(),
            'word_count': len(self.sentence_words),
            'letter_count': len(self.current_letters),
            'cooldown_remaining': max(0, self.COOLDOWN_FRAMES - self.letter_cooldown)
        }

    def reset_word(self):
        """
        Clear the current word without affecting sentence history.
        
        Example:
            builder.add_letter('W', 0.9)
            builder.add_letter('R', 0.85)
            builder.reset_word()
            print(builder.get_current_word())  # ""
        """
        self.current_word = ""
        self.current_letters = []
        self.last_letter = None
        self.letter_cooldown = 0

    def reset_all(self):
        """
        Clear everything - words, sentence, and buffers.
        
        Example:
            builder.reset_all()
            print(builder.get_full_sentence())  # ""
        """
        self.current_word = ""
        self.current_letters = []
        self.sentence_words = []
        self.last_letter = None
        self.letter_cooldown = 0
        self.confirmation_buffer = []

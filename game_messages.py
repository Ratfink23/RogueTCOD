import textwrap


class Message:
    # TODO pull these from constant?
    message_colors = {'default': [255, 255, 255],
                      'combat_damage': [255, 255, 255],
                      'combat_event': [63, 63, 63],
                      'major_death': [255, 0, 0],
                      'minor_death': [255, 127, 0],
                      'minor_effect': [63, 255, 63],
                      'map_unseen': [159, 159, 159],
                      'map_item': [255, 255, 0],
                      'minor_error': [127, 127, 255],
                      'minor_event': [63, 63, 255],
                      'major_event': [255, 0, 0],
                      'effect_damage': [255, 255, 255],
                      'effect_bonus': [0, 255, 0],
                      'targeting': [63, 63, 255]}

    def __init__(self, text, color_type='default'):
        self.text = text
        if color_type in self.message_colors:
            self.color = self.message_colors.get(color_type)
        else:
            print("DEBUG: Unknown Color {0}".format(color_type))
            self.color = self.message_colors.get('default')


class MessageLog:
    """
    Creates a message log storing all Message
    """
    def __init__(self, x, width, height):
        """
        :param x: Offset within panel
        :param width: character length before text wrap
        :param height: maximum number of messages in the log
        """
        self.messages = []
        self.x = x
        self.width = width
        self.height = height

    def add_message(self, message: Message):
        """
        Adds Message to the end of the log, and removes older message if more than message log height
        :param message: Message
        :return:
        """
        # Split the message if necessary, among multiple lines
        new_msg_lines = textwrap.wrap(message.text, self.width)

        for line in new_msg_lines:
            # If the buffer is full, remove the first line to make room for the new one
            if len(self.messages) == self.height:
                del self.messages[0]
            # Add the new line as a Message object, with the text and the color
            self.messages.append(message)

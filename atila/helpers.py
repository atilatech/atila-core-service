import random
import re
import string


def random_string(n=16, numbers_only=False):
    choices = string.digits

    if not numbers_only:
        choices += string.ascii_lowercase

    random_string_value = ''.join(random.choices(choices, k=n))

    return random_string_value


def validate_substituted_variables(check_string, raise_exception=True):
    """
    Given a string. Check to make sure that there are no variables which did not get substituted.
    This function only checks for words that contain angular braces with a word inbetween and ignores whitespaces.

    So for inline style sheets that have css styles. It will not match those provided they have a whitespace
    somewhere inside the angular brackets.
    :return:
    """

    unsubstituted_variables = re.findall(r"\{\w+}", check_string)

    if raise_exception and len(unsubstituted_variables) > 0:
        raise ValueError("There was an error with the variable substitution. "
                         f"The following unsubstituted variables were found: {unsubstituted_variables}\n"
                         f"Given the following input string: {check_string}")

    return unsubstituted_variables

from termcolor import colored
from os import system

class TicketStatus:
    registered_numbers = list()
    ticket = list()
    pattern_dict = dict()
    pattern_dict_completion_flags = dict()

    @classmethod
    def initialize(cls, registered_numbers=None, ticket=None, patterns_dict=None):
        cls.registered_numbers = registered_numbers
        cls.ticket = ticket
        cls.pattern_dict = patterns_dict
        for key in patterns_dict:
            cls.pattern_dict_completion_flags[key] = False

    @classmethod
    def print_ticket_status(cls, registered_numbers=None, ticket=None, patterns_dict=None):
        if registered_numbers is None:
            registered_numbers = cls.registered_numbers
        if ticket is None:
            ticket = cls.ticket
        if patterns_dict is None:
            patterns_dict = cls.pattern_dict

        if registered_numbers is None:
            registered_numbers_set = set()
        else:
            registered_numbers_set = set(registered_numbers)

        if len(ticket[0]) > 2:
            ljust_len = 25
        else:
            ljust_len = 5

        print(colored("My Ticket: ", "green"))
        for i, cell in enumerate(ticket):
            if (i+1) % 6 == 0:
                if cell in registered_numbers_set:
                    print(colored(cell.ljust(ljust_len), "red"))
                else:
                    print(cell.ljust(ljust_len))
            else:
                if cell in registered_numbers_set:
                    print(colored(cell.ljust(ljust_len), "red"), end=" "*8)
                else:
                    print(cell.ljust(ljust_len), end=" "*8)

        print(colored("\nPatterns and your numbers:", "green"))
        for key, value in patterns_dict.items():
            if not cls.pattern_dict_completion_flags[key]:
                print(key.ljust(20), end=" ")
                for pattern_value in value:
                    if pattern_value in registered_numbers_set:
                        print(colored(pattern_value, "red"), end=colored(" || ", "cyan"))
                    else:
                        print(pattern_value, end=colored(" || ", "cyan"))
                print("")

        remaining_for_full_house = set(cls.ticket) - registered_numbers_set
        if len(remaining_for_full_house) == 0:
            print("******************** Congratulations on winning house **********************")
        if len(remaining_for_full_house) == 1:
            print("\nJust 1 left for winning trophy, remaining ->", end=" ")
            for element in remaining_for_full_house:
                print(element)

        try:
            for k, v in cls.pattern_dict_completion_flags.items():
                if not v:
                    remaining_for_pattern_completion = cls.pattern_dict[k] - registered_numbers_set
                    if len(remaining_for_pattern_completion) == 0:
                        print(colored("\n**********************  Congratulations on winning pattern {} "
                                      "************************\n".format(k), "green"))
                        system("echo '\x1B]1337;RequestAttention=fireworks\007'")
                        cls.pattern_dict_completion_flags[k] = True
                    if len(cls.pattern_dict[k] - registered_numbers_set) == 1:
                        print("\nJust on 1 left for winning {} ->".format(k), end= " ")
                        for element in remaining_for_pattern_completion:
                            print(element)
        except:
            pass

    @classmethod
    def strike_through(cls, cell):
        result = ''
        for c in str(cell):
            result = result + c + '\u0336'
        return result


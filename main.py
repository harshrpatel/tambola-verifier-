import ast
from os import path
from os import system
import argparse
import time
import numpy as np
import tableformatter as tf
from termcolor import colored as COLO
import colored
from colored import fore, back, style, stylize
from pprint import pprint
from colorama import Back, Fore
from fireworks import run_fireworks
import constants
from util.board_stored import BoardStored
from util.board_status import BoardStatus
from util.register_input import RegisterInput
from iterfzf import iterfzf
from fuzzywuzzy import process

BACK_RESET = Back.RESET
BACK_GREEN = back.GREY_15
BACK_BLUE = back.DODGER_BLUE_2


global previous_numbers

class Checker:
    my_ticket = set()
    sorted_ticket = list()
    patterns_dict = dict()

    @classmethod
    def get_input_ticket_numbers(cls):
        first_time_flag = True
        done_with_input = False
        remove_numbers_flag = False
        while not done_with_input:
            if first_time_flag:
                response = input("Please enter the comma separated numbers here: ")
                first_time_flag = False
            else:
                response = input("Please enter the remaining numbers or numbers to remove(if chosen this option): ")
            try:
                response_list = filter(None, [int(x.strip()) for x in response.split(",")])
            except ValueError:
                response_list = filter(None, [(x.strip()) for x in response.split(",")])
            if remove_numbers_flag:
                cls.my_ticket = cls.my_ticket - set(response_list)
            else:
                cls.my_ticket = cls.my_ticket.union(set(response_list))
            cls.sorted_ticket = sorted(list(cls.my_ticket))
            print("my ticket: ", cls.sorted_ticket)
            is_done = input("Does you ticket look fine?\n1. Type yes for done\n2. no for adding more numbers\n3. "
                            "remove for removing numbers from you ticket: ")
            if is_done == "yes":
                done_with_input = True
            elif is_done == "remove":
                remove_numbers_flag = True
            else:
                remove_numbers_flag = False

    @classmethod
    def get_input_winning_patterns(cls):
        print("Now we enter the winning patterns")
        done_with_all_patterns = False
        done_with_individual_pattern = False
        while not done_with_all_patterns:
            have_more_pattens = input("Do you have patterns to add? Type yes/no: ")
            if have_more_pattens == "yes":
                done_with_individual_pattern = False
            else:
                done_with_all_patterns = True
                done_with_individual_pattern = True
            while not done_with_individual_pattern:
                pattern_name = input("Enter the pattern name: ")
                print("Ok, setting the pattern name as ", pattern_name)
                input_for_pattern_done = False
                while not input_for_pattern_done:
                    input_for_pattern = input("Enter the numbers for this pattern: ")
                    try:
                        pattern_set = set(filter(None, [int(x.strip()) for x in input_for_pattern.split(",")]))
                    except ValueError:
                        pattern_set = set(filter(None, [(x.strip()) for x in input_for_pattern.split(",")]))
                    print("does this pattern for " + pattern_name + " look fine? ", pattern_set)
                    patten_done = input("Type yes for done, if not, sorry you would have retype all the "
                                        "numbers again for this pattern: ")
                    if patten_done == "yes":
                        done_with_individual_pattern = True
                        input_for_pattern_done = True
                        cls.patterns_dict[pattern_name] = list(pattern_set)
            print(cls.patterns_dict)

    @classmethod
    def generate_ticket_txt(cls):
        with open("my_ticket.txt", "w") as wfile:
            wfile.write(str(cls.my_ticket)+"\n")
            wfile.write(str(cls.sorted_ticket)+"\n")
            wfile.write(str(cls.patterns_dict))

    @classmethod
    def pass_the_variables_from_file(cls, ticket_from_file=None, sorted_from_file=None, patterns_from_file=None):
        if ticket_from_file is None:
            ticket_from_file = set()
        if sorted_from_file is None:
            sorted_from_file = list()
        if patterns_from_file is None:
            patterns_from_file = dict()
        cls.my_ticket = ticket_from_file
        cls.sorted_ticket = sorted_from_file
        cls.patterns_dict = patterns_from_file

    @classmethod
    def print_status(cls, ticket=None, patterns=None):
        if ticket is None:
            ticket = cls.sorted_ticket
        if patterns is None:
            patterns = cls.patterns_dict

        print("My Ticket: ")
        for i, num in enumerate(ticket):
            if i in [4, 9, 13, 18, 23]:
                print(str(num).zfill(2))
            elif i == 12:
                print("X " + " " * 8 + str(num).zfill(2), end=" " * 8)
            else:
                print(str(num).zfill(2), end=" " * 8)

        print("\nPatterns and your numbers")
        for k, v in patterns.items():
            print(k, end=" ")
            print(v)


class FileStorage:
    stored_my_ticket = set()
    stored_sorted_ticket = list()
    stored_patterns_dict = dict()

    @classmethod
    def get_from_file(cls, file_path):
        with open(file_path, "r") as rfile:
            lines = rfile.readlines()
            for line in lines:
                obj = ast.literal_eval(line)
                if isinstance(obj, set):
                    cls.stored_my_ticket = obj
                elif isinstance(obj, list):
                    cls.stored_sorted_ticket = obj
                elif isinstance(obj, dict):
                    cls.stored_patterns_dict = obj


class Verify:

    def __init__(self, sorted_ticket, my_ticket, input_num, pattern_dict=None):
        self.ticket = my_ticket
        self.variations = pattern_dict
        self.input_num = input_num
        # if file_name:
        #     self.file_name = file_name
        self.remaining_ticket = sorted_ticket

    def get_remaining_ticket(self):
        try:
            self.input_num = int(self.input_num)
        except ValueError:
            self.input_num = self.input_num
        if self.input_num in self.remaining_ticket:
            self.remaining_ticket.remove(self.input_num)
        np_remained = np.array(self.remaining_ticket)
        if len(self.remaining_ticket) == 0:
            print(fore.GREEN + "Congratulations on winning full house!")
            run_fireworks()
            exit(0)
        # print(np_remained)
        # print(tf.generate_table(np_remained), grid_style=tf.AlternatingRowGrid(BACK_GREEN, BACK_BLUE))

    def get_scratched_ticket(self):
        new_tkt = self.ticket
        self.ticket = [strike_through(x) if x in list(set(self.ticket) - set(self.remaining_ticket)) else "\033[1;31m"+str(x)+"\033[1;31m" for x in new_tkt]
        np_ticket = np.array(self.ticket)
        shape = constants.NUMPY_SHAPE[len(self.ticket)]
        np_ticket = np_ticket.reshape(shape[0], shape[1])
        print(tf.generate_table(np_ticket, grid_style=tf.AlternatingRowGrid(BACK_GREEN, BACK_BLUE)))

    def check_variations(self):
        remaining_variation = {}
        try:
            self.input_num = int(self.input_num)
        except ValueError:
            self.input_num = self.input_num
        try:
            for i in self.variations:
                if self.input_num in self.variations[i]:
                    self.variations[i].remove(self.input_num)
                remaining_variation[i] = self.variations[i]
                if len(remaining_variation[i]) == 1:
                    print(fore.LIGHT_BLUE + "Almost there, only one number remaining to claim variation",
                          style.RESET, fore.RED, style.BOLD, "{}: {}".format(i, remaining_variation[i]), style.RESET,
                          "\n")
                if not done_variation[i]:
                    if len(remaining_variation[i]) < 1:
                        done_variation[i] = True
                        print(fore.GREEN, style.BOLD,
                              "Congratulations, for your ticket variation {} is successfully done!".format(i) + style.RESET,
                              "\n")
                        del remaining_variation[i]
            key_format = "\033[1;32m"
            value_format = "\033[1;34m"

            for key, value in remaining_variation.items():
                # print(fore.BLACK, back.DODGER_BLUE_2, key, fore.BLACK, value, style.RESET)
                print("{}{} {}{}".format((key_format+key).ljust(20), '\t', value_format, value))

        except Exception as err:
            print(err)


def strike_through(num) -> str:
    result = ''
    for c in str(num):
        result = result + c + '\u0336'
    return result


def print_board(numbers_called, board_list):
    system("clear")
    print("BOARD")
    print("*******", BOARD_CONFIG, "*******")
    # board_list = [f'{Fore.GREEN}{str(ele)}' if ele in numbers_called else f'{Fore.RED}{str(ele)}' for ele in board_list]
    # import textwrap
    # wrapped_board_list = ['\n'.join(textwrap.wrap(board)) for board in board_list]
    # board_list = ["\033[0;32m"+str(x)+"\033[0;32m" if str(x) in numbers_called else "\033[1;31m"+str(x)+"\033[1;31m" for x in wrapped_board_list]
    board_list = [f'{Fore.GREEN}{str(ele)}' if ele in numbers_called else f'{Fore.BLUE}{str(ele)}' for ele in board_list]
    # board_list = [f'\033[3{str(ele)}m\033[0m' if ele in numbers_called else f'{Fore.RED}{str(ele)}' for ele in board_list]

    # c = Fore.GREEN
    # np.set_printoptions(formatter={'float': f'{c}{x}'})
    np_board = np.array(board_list)
    # print(np_board)
    final_board = np_board.reshape(10, 9)
    from tabulate import tabulate
    # tabulate.PRESERVE_WHITESPACE = False
    # tabulate.WIDE_CHARS_MODE = True
    tt = tabulate(final_board, tablefmt="fancy_grid")
    # tt = tabulate(final_board, tablefmt="html")
    # with open("board.html", "w") as fd:
    #     fd.write(tt)
    print(tt)
    # back_col = back.GREY_15
    # back_col_alt = back.DODGER_BLUE_2
    # print(tf.generate_table(final_board, grid_style=tf.AlternatingRowGrid(back_col, back_col_alt)))

    # for i, ele in enumerate(board_list):
    #     if str(ele) in numbers_called:
    #         if i % 9 == 0:
    #             print(fore.GREEN, str(ele).ljust(5))
    #         else:
    #             print(fore.GREEN, str(ele).ljust(5), end=" " * 8)
    #     else:
    #         if i % 9 == 0:
    #             print(fore.RED, str(ele).ljust(5))
    #         else:
    #             print(fore.RED, str(ele).ljust(5), end=" " * 8)


def main():
    checker = Checker()
    fileStored = FileStorage()
    continue_with_existing_ticket = False

    if path.exists("my_ticket.txt"):
        print("There seems to be a ticket already generated :) ")
        fileStored.get_from_file("my_ticket.txt")
        checker.print_status(fileStored.stored_sorted_ticket, fileStored.stored_patterns_dict)
        check_for_valid_ticket = input("is this your ticket? type yes to confirm and no to generate a new ticket: ")
        if check_for_valid_ticket == "yes":
            continue_with_existing_ticket = True

    if continue_with_existing_ticket:
        checker.pass_the_variables_from_file(
            fileStored.stored_my_ticket,
            fileStored.stored_sorted_ticket,
            fileStored.stored_patterns_dict)
    else:
        print("Lets generate a new ticket for you")
        checker.get_input_ticket_numbers()
        checker.get_input_winning_patterns()
        checker.generate_ticket_txt()
    checker.print_status()
    my_ticket = checker.my_ticket
    my_ticket = constants.ticket
    sorted_list = checker.sorted_ticket
    variation_dict = checker.patterns_dict
    game_not_ended = True
    global done_variation
    done_variation = dict.fromkeys(variation_dict.keys(), False)
    previous_numbers = []
    if BOARD_CONFIG is not None:
        BoardStored.get_from_file(BOARD_CONFIG)
        board_list = BoardStored.my_stored_board
        BOARD_TYPE = "custom"
    else:
        board_list = range(1, 91)
        BOARD_TYPE = "regular"
    reg_input = RegisterInput()
    reg_input.initialize(current_board=board_list, ticket=sorted_list)

    while game_not_ended:
        input_num = input("Enter any number:")
        if input_num == "bye":
            game_not_ended = False
            exit(0)
        if str(input_num) in variation_dict.keys():
            del variation_dict[str(input_num)]
            continue
        if BOARD_TYPE is "regular" and input_num != "board":
            if int(input_num) in board_list:
                input_num = input_num
        else:
            if input_num in board_list:
                input_num = input_num
            else:
                input_num_list = process.extractBests(input_num, board_list, limit=3, score_cutoff=80)
                f_dict = dict()
                if len(input_num_list) > 0:
                    for i, t in enumerate(input_num_list):
                        f_dict[i + 1] = t[0]
                    for k, v in f_dict.items():
                        print("type {} for {}".format(k, v))
                    input_from_fuzzy = int(input(COLO("\ntype your choice here or 0 for none: ", "blue")))
                    if input_from_fuzzy == 0:
                        pass
                    else:
                        input_num = f_dict[input_from_fuzzy]
            # input_num = iterfzf(board_list, multi=False, extended=False)
        system("clear")
        previous_numbers.append(input_num)
        if input_num == "board":
            print_board(previous_numbers, board_list)
            continue
        print(fore.LIGHT_BLUE, style.BLINK, "Numbers called out so far: ", previous_numbers[::-1], style.RESET, "\n")
        verify = Verify(sorted_list, list(my_ticket), input_num, pattern_dict=variation_dict)
        verify.get_remaining_ticket()
        # verify.get_scratched_ticket()
        verify.check_variations()
        verify.get_scratched_ticket()
    print("Game has ended!\n")


def arg_builder():
    parser = argparse.ArgumentParser(description='KuTe test framework for Yellowstone cluster', prog='kute.py')
    parser.add_argument('--boardconfig',
                        help='board config file to get customized housie board')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = arg_builder()
    BOARD_CONFIG = args.boardconfig
    main()

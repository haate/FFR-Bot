from typing import *


add_option_wrong_format = "you passed the incorrect number of parameters"
already_voted = "it looks like you already voted"
cannot_convert_to_int = "there was an error converting a string to an integer"
cannot_vote_poll_closed = (
    "this poll is not open, it either must first be "
    "started before voting, or this poll has ended "
)
cant_find_poll = "sorry, I cannot find a poll with that id, please try again"
confirm_end_poll = (
    "Are you sure you want to end this poll?\nNo more votes "
    "will be able to be cast and the results will be "
    "calculated, to, proceed, reply `yes` to stop, type `no` "
)
confirm_vote = (
    "Respond with a `yes` if your vote is correct or respond "
    "with a `no` if it is not. \nYour vote:"
)
invalid_poll_type = "That isn't a valid poll type, please try again"
invalid_vote_option = "that option doesnt exist, please try again"
no_poll_in_channel = "this channel doesn't have a poll running"
not_enough_options = (
    "there are less than two options for people to vote "
    "on!\n\nHere are the current options:\n\n"
)
not_in_server_long_enough = (
    "This discord account has not been in the "
    "server for long enough to vote."
)
only_mention_one = "You must mention exactly one person per command"
option_already_exists = "that option already exists"
poll_already_ended = "this poll has already ended"
poll_already_started = "this poll has already started"
poll_not_started = "this poll has not started yet"
poll_now_closed = "The poll has now been closed."
stv_submit_text = (
    "To vote in this poll, rank the available options "
    "starting at 1, copy and paste the following, and replace "
    "the <x>s with your ranking (or leave the <x>s there if "
    "you dont want to rank them):"
)
timeout = "Two minute timeout reached, please enter the original command again"
vote_not_processed = "your vote has not been processed, please try again"
vote_processed = "your vote has been processed"
not_in_server = "you were not found in the server."
poll_still_open = "the poll is still open."


category_not_found = "The bot could not find the category for this channel."
role_requests_channel_not_set = "The role requests channel was not set."
roles_added = "Self-Assignable roles added"
roles_removed = "Self-Assignable roles removed"
roles_not_added = "Self-Assignable roles not added"
roles_not_removed = "Self-Assignable roles not removed"
roles_look_ok_added = (
    "Do the following self assignable roles look correct? Reply "
    'with "yes" or "no"'
)
roles_look_ok_removed = (
    "Do the following self assignable roles look correct? Reply "
    'with "yes" or "no"'
)
add_self_assignable_role_arg_count_off = (
    "The number of role names and descriptions passed to this command"
    "is not even, did you forget one, or are you missing quotes?"
)

self_assignable_role_message = (
    "To add or remove one of the following roles, click on the reaction on the"
    "message for the role you want to add or remove"
)


cleaning_up_stale_roles = (
    "Removing stale roles/descriptions from the bot database at this point if"
    " any exist."
)


def role_message(name, description):
    return f"Role name: {name}\nRole description: {description}"


def account_age(user_age, required_age):
    return (
        "this discord account is "
        + str(user_age)
        + " days old, your account must be at least "
        + str(required_age)
        + " days old."
    )


set_twitch_id_not_found = (
    "No twitch id was found, did you forgot to add it after"
    " the command name?"
)

get_twitch_id_not_found = "No twitch id was found for this user"

delete_user_data_yes_no = (
    "Are you sure you want to delete all bot saved user"
    " data?\nRespond with yes or no"
)


def list_people_no_twitch_id_set(names: List[str]):
    msg = "The following people don't have their twitch id set: "
    for name in names:
        msg += name + ", "
    msg = msg[:-2]
    return msg

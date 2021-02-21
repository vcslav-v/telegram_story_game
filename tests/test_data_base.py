"""Tests data_base app."""
import os

os.environ['DB'] = 'localhost:5432'
os.environ['DB_PASSWORD'] = 'mysecretpassword'

from data_base import main


def test_get_user_or_make_if_new():
    """Test func get_user_or_make_if_new."""
    user = main.get_user_or_make_if_new(1)
    assert user.telegram_id == 1

    user = main.get_user_or_make_if_new(2)
    assert user.telegram_id == 2

    user_same = main.get_user_or_make_if_new(2)
    assert user is user_same

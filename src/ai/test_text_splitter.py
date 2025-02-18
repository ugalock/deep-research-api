import pytest
from langchain.text_splitter import RecursiveCharacterTextSplitter

def test_split_text_by_separators():
    splitter = RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=10)
    text = "Hello world, this is a test of the recursive text splitter."
    expected = ["Hello world", "this is a test of the recursive text splitter"]
    result = splitter.split_text(text)
    assert result == expected

    splitter.chunk_size = 100
    text2 = (
        "Hello world, this is a test of the recursive text splitter. "
        "If I have a period, it should split along the period."
    )
    expected2 = [
        "Hello world, this is a test of the recursive text splitter",
        "If I have a period, it should split along the period."
    ]
    result2 = splitter.split_text(text2)
    assert result2 == expected2

    splitter.chunk_size = 110
    text3 = (
        "Hello world, this is a test of the recursive text splitter. "
        "If I have a period, it should split along the period.\n"
        "Or, if there is a new line, it should prioritize splitting on new lines instead."
    )
    expected3 = [
        "Hello world, this is a test of the recursive text splitter",
        "If I have a period, it should split along the period.",
        "Or, if there is a new line, it should prioritize splitting on new lines instead."
    ]
    result3 = splitter.split_text(text3)
    assert result3 == expected3

def test_empty_string():
    splitter = RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=10)
    result = splitter.split_text("")
    assert result == []

def test_special_characters_and_large_texts():
    splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=10)
    large_text = "A" * 1000
    expected = ["A" * 200] * 5
    result = splitter.split_text(large_text)
    assert result == expected

    special_char_text = "Hello!@# world$%^ &*( this) is+ a-test"
    expected_special = ["Hello!@#", "world$%^", "&*( this)", "is+", "a-test"]
    result_special = splitter.split_text(special_char_text)
    assert result_special == expected_special

def test_invalid_configuration():
    with pytest.raises(ValueError, match="Cannot have chunkOverlap >= chunkSize"):
        RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=50)

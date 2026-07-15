from main import start

def test_answer():
    assert start("What is 1.1 + 2.2") == '{"name":"fn_add_float","parameters":{"a":1.1,"b":2.2}}'
    assert start("What is -1.1 + 2.2") == '{"name":"fn_add_float","parameters":{"a":-1.1,"b":2.2}}'
    assert start("Greet Mia") == '{"name":"fn_greet","parameters":{"name":"Mia"}}'

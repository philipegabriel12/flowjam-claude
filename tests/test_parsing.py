from decimal import Decimal

from flowjam.pay import parse_duration, pay_for
from flowjam.projects import parse_project_message

R = Decimal(25)


def test_pay_prorated_to_second():
    assert pay_for(parse_duration("4:00:00"), R) == Decimal("100.00")
    assert pay_for(parse_duration("4:30:00"), R) == Decimal("112.50")
    assert pay_for(parse_duration("0:00:36"), R) == Decimal("0.25")
    assert pay_for(parse_duration("1:30"), R) == Decimal("37.50")


def test_project_messages_from_discord():
    cases = {
        "https://drive.google.com/drive/folders/1h6Du8sbik-xNyABrBqyVYKHlMQKKVval?usp=sharing\nVisma x Flowjam - Collect + Render\n@liveira": "Visma",
        "https://drive.google.com/drive/folders/1zqi3vFRBazwkS5S0EDwH9vLXZVLDmFoX?usp=sharing\n\nMecka x Flowjam\n\n@liveira": "Mecka",
        "Flowjam x Popp\nhttps://drive.google.com/drive/folders/abc_DEF-1": "Popp",
    }
    for text, project in cases.items():
        [link] = parse_project_message("1", text)
        assert link.project == project
        assert link.target_folder == f"Flowjam x {project}"


def test_message_without_link():
    assert parse_project_message("1", "@liveira Link atualizado") == []

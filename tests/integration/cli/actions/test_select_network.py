import pytest

from nucypher.blockchain.eth.domains import TACoDomains
from nucypher.cli.actions.select import select_domain

__DOMAINS = TACoDomains.SUPPORTED_DOMAIN_NAMES


@pytest.mark.parametrize("user_input", range(0, len(__DOMAINS) - 1))
def test_select_network_cli_action(test_emitter, capsys, mock_stdin, user_input: int):
    mock_stdin.line(str(user_input))
    selection = __DOMAINS[user_input]
    result = select_domain(emitter=test_emitter)
    assert result == selection
    captured = capsys.readouterr()
    for name in __DOMAINS:
        assert name in captured.out
    assert mock_stdin.empty()

import pytest

from nucypher.blockchain.eth.agents import CoordinatorAgent
from nucypher.blockchain.eth.signers.software import Web3Signer
from nucypher.crypto.powers import TransactingPower

FAKE_TRANSCRIPT = b'(\x01\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x0br8\xa5\xc0\x1e55\xea\xac\'?r\xd5\xa6\x16\x11\xec\xca^\x0c,\x999\xc9\x82\x1f\xb8\xe5^\xdb\x11O\xb9\xbd1\xae\x02p"\x04\xe7\xab\x04K\x1fv9\x0e\xea"\xa0\xc5_/#\xf1\x1e{Qc\xfb\xed\x18\\H73.\xcd2q3d%\xaa,b\x19\x85}\xa9\xf5\xbe\xd6\x01\xc96\xcf\x0b\xaaji\x1e\xaf!\x0e\x1e;\x07K\xbd\x81\x8f\xbd\xae\x8b\xa0Li}\xd6oU\xa1d\xf2\x02\x8bT\x86X\x8b\x05\xf5\x1e\xf9\x9f~\xcc\x88+L!h\x15\x87\xfa\xbfvy3\xb6J\x0e\x13I\xad\xc5\xdczG\xfbQ\x8f4\x1aU#\xa1]\xc0sbJ!n\x1b\x8e\xa0\xce\xc8\xba\x08\x15xr\xd2\xcd:i\xb2\xab\x01\x9a\xe5wk\x845\xe6,\x11f\x19\x06w\xf1\xd5a\x83\x82\xdf\x96k\xben\xc9\xa2\x81i\x81\xd3Y\xb2\x91\x19]\xd3\x976\xdb\x19\x08%\xc0\x8f4\xf1c6\xd4\xc4)\x9a\xf7 [\xd6\x88\x13IA%@r=\xf7s\xebt\xd5\xdd\xec\x84\xcb!\xc6] \xfe7g\x8e\x00\x12\x0b\nO\t\x95\xb3\xe0tdI\xc0d\x8b\'\xd3|\xc5@\xac]\xabk\x08\x03\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00n\xcc\xab\t7\xbf\x1e\xc9\xeb\xbd\x0cvEY\x0cf\'\tta\x93\x91\xc9\xce\x83H\xa4\xef\xbb\x16\xc4tb%V\x80\xd0\xc6\x02\x1ca]\xc1\xa2\xe3\xb89\x16\xac\x9d>\xa3\xbe\x86R\xf4\xefj\xdf&\xbcw\xe2\xda\x93t/\xf9\xacK\xb1d\xc0w\xee\x07\xe36\x9a\x0c\xa5\xc8\x9c\xb7\xe4\xd5\x91\xed\xccI\xdc\xf4NU\x7f\r*\xad\x07\xe38\x0b[N\x96\xff\xb4\'\xe1[o\xc4\x0f\xd1\xe3]\x05y\x89\xa7\xe8\xa8Zat6M\xa8\xbe\x9d\x15\xaa\xdch\xa3&\xd6\xe3l\xaa\xf0\xb3>\x0c\x06\xa8\xc6U\xe4\x08\x17?\x8cd\xaa\xcf\xcas\xd7\xdb\x98\xc62\xae\x93:}:wm0\xc9\x98L\xed4\xeau+=B\x13\xe2#bho\n1"\xbd\x012\n\xceH\x18n\xce\x1c_"k\xeaH\xd0\xc3\xfa\x98\xf1 \x7fJ\xd0x\xf9M~\xd0JE\x8c\xfc\x9e\xe6\xff\xdd<\xcb\x10\xf6c5/@zzyO\t\x9e\x1dU\xcc\x18\xba\xd6\xb3y\xa8\nN\x1e(\x9f\x00\xbd\x87f\xfeG\xd8\xe6\xd9\xee\x06\x1bFp\xbd\xec\xca\xd9J\xd5-\xed\xce\xfc\xec\x07u\x86\xc3\xdc\xd3\xc6\x03\xf7\x9f6>\xb6"5J\x1ds\xf2\x10\x1df\xe2\xbf\xa8>\x10\x07\n\x15\xd2\xf41\xea\xaf\xbb+bk,iCd\xef\x9e\x04q\xedA\x9aOB\x8c\x81\x82\x02\xd9E\x8dv\xac\xcb\x02\xad0-\x9er\x8d<\x92\xf2\xdc\xaf\xb5:/\xd6\xad\xa7\xe7N\xb8> M\xb3\x9f\n\xeeH\x01r\x9b\xca\xf2\x96\'\xcd@\x12\xe9\n\x05\xcb\x8a\x94\xc3\xe6\x16wo]\xb4\xac\xeb\xa5S\xc08,\xa9(06)\x9d\x84\x85_\xe0\xb4\xef\x18\xa0\xf2eO\xfc7\x18\xa6h\x94\xefA\xd91\xeeW\xcd\x15\x96\x02\xa0\x11\x01\xb9j\xa8\xcf|h\x9c\\\xe8r\x9e\xa6*;\x02\xf3\xb7qS\\FX\xc7\xd6\xfew\xf0\xf4\x12w\xfb\xc6\xcc\xba8\x90\xa1\x96JckV\x01\xdc7\x972\x9bo_\xaf{\x13Jlg\x0b\x87\xbe\xbb\rW\x89?\x1c^b5\x12\xc3\x98\xecv!\x0c\xa9\x98w\x9c\xb6\xb3\x00p]\'.\xdcp\xae\x1e\x0e\x0579B\x9a\xab\xf2k\x1e\x07\x1c7\xe7\xafp\x82\x90XTX\xfe\x14\xeab|&\xebT\xd8\x000\x19\xeb\xb6a\x93K\xbd\xa0\xa0\x1a\x8d\'\x0e\x816Y\x14\x8e3\x1a\xfaS:}?m\\\xbc\xb0\xfb\xe7+\xe2\x87\x07\xec\x9e\x02\x1en/\xeb\x14\x1e\xf2\x03\x18=\xb2\x9c\xb4XP\x11\xee\xbe"M\x0e\xbd8&Zd\x0c\xfe\xb3e%\x80\x95\xc2b\xa0<\x16&\xc6\xcf#ItX\xe2\\H\x06\xf9q\xd5\x97\xdeD\xfb\xa2\x12W?\x03\x84\xa9\xbe#\xf2\xa0\xb8\x8c$\xc3\x130\x94\x18?\x1fL\x9b\x99|\xad\xc69+\xe4ma\x00\xbc\xf5Ta \xfc\x17\x8c5\xc6\xbd\xf0HA\xe7\x11\xd7\x85\xdf{WO5N{#\xe1\xd4\xd7\x84\xad\xc6N\t\x05\x99.)\x1fB\xce\xd4O\xdf;\xfcZ\xe8\r\xc0\xaf\xc6\xf8$\xf4rH\xa1d\xba\xf8\r+\xd5nk\x029N\x1bD\xdfz8\'M\x13\xe7v\xd3\xef\xc0\x00\x00\x00\x00\x00\x00\x00\x05\xc8\x14\x1d\xc6\x90\xc5\xc9\xf2\xcfKK&%\x0c\xe0\xb4[:\x8e\x0bc7\x97\x92\xb2\xb6^c}\x1d\x98\x1e%\xfdO4\xf2\xc9\xe4*Y\x05\xb7F\xfd\xd7+\x18T\x04\xf8+\xab\x94\xfe\xe4\xcc\xc1\xed\xe5e\x8c\x95\x89\x88\x90z\xe1Z!\xb3\x8c\x98\xb5*\xee\xce\xda\xf4\xd2\x04\xa0\x16\x9a\x1e\xe3b?\x1b\xb4\x90\xf5\xa0\x19\xa8\x13d \xd78\x90\xf0\xc1JTu?\xad\xb5\x81\x1a\x1a\xb7\x07$\xf3\x03\xdc\x11O_\xc0Oz\xd5\xbbiD4\xf1\xf4\xbe\x9d}\xa3\x99\xff\xb3\xf4,\xccf\xce\x13\x90\x12\x1e\x1a\xe5\xc3_\xf2\x11e"\x15`\x1fz\x8dS\xb8\xd7\x0c\x8dD`\x7f\xed\xe09\xef\xa2`\xb2Q\x15GE\xabI4$\x9a\x0c\xa5\xec1\xac\xc3\xe5'


@pytest.fixture(scope='module')
def agent(mock_contract_agency) -> CoordinatorAgent:
    coordinator_agent: CoordinatorAgent = mock_contract_agency.get_agent(CoordinatorAgent, registry=None)
    return coordinator_agent


@pytest.fixture(scope='module')
def cohort(ursulas):
    return [u.checksum_address for u in ursulas[:4]]


@pytest.fixture(scope='module')
def ursula(ursulas):
    return ursulas[1]


@pytest.fixture(scope='module')
def transacting_power(testerchain, alice):
    return TransactingPower(account=alice.transacting_power.account, signer=Web3Signer(testerchain.client))


def test_initiate_ritual(agent: CoordinatorAgent, cohort, transacting_power):
    receipt = agent.initiate_ritual(
        nodes=cohort,
        transacting_power=transacting_power
    )

    participants = [CoordinatorAgent.Ritual.Participant(
        node=c,
    ) for c in cohort]

    ritual = CoordinatorAgent.Ritual(
        id=0,
        initiator=transacting_power.account,
        dkg_size=4,
        init_timestamp=123456,
        participants=participants,
    )
    agent.get_ritual = lambda *args, **kwargs: ritual
    agent.get_participants = lambda *args, **kwargs: participants

    assert receipt['transactionHash']
    number_of_rituals = agent.number_of_rituals()
    ritual_id = number_of_rituals - 1
    return ritual_id


def test_perform_round_1(ursula, random_address, cohort):
    ursula.ritual_tracker.refresh(fetch_rituals=[0])
    ursula.perform_round_1(
        ritual_id=0, initiator=random_address, nodes=cohort, timestamp=0
    )


def test_perform_round_2(ursula, cohort, transacting_power, agent, mocker):
    mocker.patch('nucypher.crypto.ferveo.dkg._validate_pvss_aggregated', return_value=True)
    participants = [CoordinatorAgent.Ritual.Participant(
        node=c,
        aggregated=False,
        transcript=FAKE_TRANSCRIPT
    ) for c in cohort]
    ritual = CoordinatorAgent.Ritual(
        id=0,
        initiator=transacting_power.account,
        dkg_size=4,
        init_timestamp=123456,
        total_transcripts=4,
        participants=participants,
    )
    agent.get_ritual = lambda *args, **kwargs: ritual
    agent.get_participants = lambda *args, **kwargs: participants
    agent.get_ritual_status = lambda *args, **kwargs: 2

    ursula.perform_round_2(ritual_id=0, timestamp=0)

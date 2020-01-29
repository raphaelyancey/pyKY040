import unittest
from unittest.mock import patch, Mock, MagicMock

MockRPi = MagicMock()
modules = {
    "RPi": MockRPi,
    "RPi.GPIO": MockRPi.GPIO,
}
patcher = patch.dict("sys.modules", modules)
patcher.start()

import pyky040


class TestEncoder(unittest.TestCase):

    def test_types(self):
        """
        Tests if it raises an exception if arguments are missing or of the wrong type.
        """
        self.assertRaises(BaseException, pyky040.Encoder, DT=3)
        self.assertRaises(BaseException, pyky040.Encoder, SW=3)
        self.assertRaises(BaseException, pyky040.Encoder, CLK=3)
        self.assertRaises(BaseException, pyky040.Encoder, CLK=17, SW=3)
        self.assertRaises(BaseException, pyky040.Encoder, SW=17, DT=3)
        self.assertRaises(BaseException, pyky040.Encoder, SW=17, DT=3, CLK='foobar')
        self.assertRaises(BaseException, pyky040.Encoder, SW=17, CLK=3, DT='foobar')
        self.assertRaises(BaseException, pyky040.Encoder, CLK=17, DT=3, SW='foobar')

    def test_callbacks_calls(self):
        """
        Tests if the increase callback is called on clockwise rotation.
        """
        inc_mock = Mock()
        dec_mock = Mock()
        chg_mock = Mock()

        encoder = pyky040.Encoder(DT=1, CLK=2)
        encoder.setup(inc_callback=inc_mock, dec_callback=dec_mock, chg_callback=chg_mock)

        encoder._clockwise_tick()
        inc_mock.assert_called_once()
        chg_mock.assert_called_once()
        dec_mock.assert_not_called()

        for m in [inc_mock, dec_mock, chg_mock]:
            m.reset_mock()

        encoder._counterclockwise_tick()
        dec_mock.assert_called_once()
        chg_mock.assert_called_once()
        inc_mock.assert_not_called()

    def test_scale_mode(self):
        """
        Tests the scale mode.
        """

        encoder = pyky040.Encoder(DT=1, CLK=2)
        encoder.setup(chg_callback=lambda count: None, scale_min=33, scale_max=40)

        self.assertEqual(encoder.counter, 33)

        encoder._clockwise_tick()
        self.assertEqual(encoder.counter, 34)

        for _ in range(0, 6):
            encoder._clockwise_tick()
        self.assertEqual(encoder.counter, 40)

        encoder._clockwise_tick()
        self.assertEqual(encoder.counter, 40)

        for _ in range(0, 9):
            encoder._counterclockwise_tick()
        self.assertEqual(encoder.counter, 33)

        encoder = pyky040.Encoder(DT=1, CLK=2)
        encoder.setup(chg_callback=lambda count: None, scale_min=33.4, scale_max=40.2)

        self.assertEqual(encoder.counter, 33.4)

        encoder._clockwise_tick()
        self.assertEqual(encoder.counter, 34.4)

        for _ in range(0, 6):
            encoder._clockwise_tick()
        self.assertEqual(encoder.counter, 40.2)

        encoder._clockwise_tick()
        self.assertEqual(encoder.counter, 40.2)

        for _ in range(0, 9):
            encoder._counterclockwise_tick()
        self.assertEqual(encoder.counter, 33.4)

        encoder = pyky040.Encoder(DT=1, CLK=2)
        encoder.setup(chg_callback=lambda count: None, scale_min=30, scale_max=40, loop=True)

        for _ in range(0, 10):
            encoder._clockwise_tick()
        self.assertEqual(encoder.counter, 40)

        encoder._clockwise_tick()
        self.assertEqual(encoder.counter, 30)

        encoder._counterclockwise_tick()
        self.assertEqual(encoder.counter, 40)


if __name__ == '__main__':
    unittest.main()

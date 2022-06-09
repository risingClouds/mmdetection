# Copyright (c) OpenMMLab. All rights reserved.
import unittest
from unittest import TestCase

import torch
from parameterized import parameterized

from mmdet import *  # noqa
from mmdet.core import DetDataSample
from .utils import demo_mm_inputs, get_detector_cfg


class TestKDSingleStageDetector(TestCase):

    # TODO: waiting ``ld/ld_r18_gflv1_r101_fpn_coco_1x.py`` ready
    @parameterized.expand(['lad/lad_r101_paa_r50_fpn_coco_1x.py'])
    def test_init(self, cfg_file):
        model = get_detector_cfg(cfg_file)
        model.backbone.init_cfg = None

        from mmdet.models import build_detector
        detector = build_detector(model)
        assert detector.backbone
        assert detector.neck
        assert detector.bbox_head
        assert detector.device.type == 'cpu'

    @parameterized.expand([('lad/lad_r101_paa_r50_fpn_coco_1x.py', ('cpu',
                                                                    'cuda'))])
    def test_single_stage_forward_train(self, cfg_file, devices):
        model = get_detector_cfg(cfg_file)
        model.backbone.init_cfg = None

        from mmdet.models import build_detector
        assert all([device in ['cpu', 'cuda'] for device in devices])

        for device in devices:
            detector = build_detector(model)

            if device == 'cuda':
                if not torch.cuda.is_available():
                    return unittest.skip('test requires GPU and torch+cuda')
                detector = detector.cuda()

            assert detector.device.type == device

            packed_inputs = demo_mm_inputs(2, [[3, 128, 128], [3, 125, 130]])

            # Test forward train
            losses = detector.forward(packed_inputs, return_loss=True)
            assert isinstance(losses, dict)

            # Test forward_dummy
            batch = torch.ones((1, 3, 64, 64)).to(device=device)
            out = detector.forward_dummy(batch)
            assert isinstance(out, tuple)
            assert len(out) == 3

    @parameterized.expand([('lad/lad_r101_paa_r50_fpn_coco_1x.py', ('cpu',
                                                                    'cuda'))])
    def test_single_stage_forward_test(self, cfg_file, devices):
        model = get_detector_cfg(cfg_file)
        model.backbone.init_cfg = None

        from mmdet.models import build_detector
        assert all([device in ['cpu', 'cuda'] for device in devices])

        for device in devices:
            detector = build_detector(model)

            if device == 'cuda':
                if not torch.cuda.is_available():
                    return unittest.skip('test requires GPU and torch+cuda')
                detector = detector.cuda()

            assert detector.device.type == device

            packed_inputs = demo_mm_inputs(2, [[3, 128, 128], [3, 125, 130]])

            # Test forward test
            detector.eval()
            with torch.no_grad():
                batch_results = detector.forward(
                    packed_inputs, return_loss=False)
                assert len(batch_results) == 2
                assert isinstance(batch_results[0], DetDataSample)
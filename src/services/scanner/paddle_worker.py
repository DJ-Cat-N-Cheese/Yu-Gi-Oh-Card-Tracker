import logging
import sys
import os
import time
import json
import traceback

# Configure logging for the worker process
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('PaddleWorker')

def run_paddle_ocr(image_path, use_angle_cls, enable_mkldnn, lang='en', ocr_version='PP-OCRv4', use_gpu=False):
    """
    Worker function to run PaddleOCR in a separate process.
    """
    try:
        import cv2
        import paddle
        from paddleocr import PaddleOCR

        # Verify GPU availability
        if use_gpu:
            if not paddle.device.is_compiled_with_cuda():
                logger.warning("GPU requested but Paddle is not compiled with CUDA. Falling back to CPU.")
                use_gpu = False
            else:
                logger.info("PaddleOCR using GPU.")

        # Explicitly set environment for reliability?
        # os.environ["FLAGS_allocator_strategy"] = 'auto_growth'

        # Set device globally (Newer PaddleOCR versions might not accept use_gpu arg)
        try:
            device = "gpu" if use_gpu else "cpu"
            paddle.device.set_device(device)
            logger.info(f"Set Paddle device to {device}")
        except Exception as e:
            logger.warning(f"Failed to set Paddle device: {e}")

        logger.info(f"Initializing PaddleOCR (GPU: {use_gpu}, Angle: {use_angle_cls}, MKLDNN: {enable_mkldnn}, Ver: {ocr_version})")

        # Initialize PaddleOCR with explicit version to avoid unstable defaults
        # Removed use_gpu and show_log args which cause ValueError in newer versions
        ocr = PaddleOCR(
            use_angle_cls=use_angle_cls,
            lang=lang,
            enable_mkldnn=enable_mkldnn,
            ocr_version=ocr_version
        )

        image = cv2.imread(image_path)
        if image is None:
            return {"error": "Failed to load image"}

        # Resize if huge (CPU optimization)
        h, w = image.shape[:2]
        if w > 2000 or h > 2000:
            logger.info("Resizing huge image for CPU safety")
            scale = 1600 / max(w, h)
            image = cv2.resize(image, (0, 0), fx=scale, fy=scale)

        # Run OCR
        # cls parameter must match use_angle_cls config for best results
        result = ocr.ocr(image, cls=use_angle_cls)

        # Parse result to simple JSON-serializable format
        # structure: [ [ [[x,y]..], (text, conf) ], ... ]
        parsed_result = []

        if result and result[0]:
            for line in result[0]:
                if len(line) < 2: continue
                # line[1] is (text, conf)
                txt_element = line[1]
                if isinstance(txt_element, (list, tuple)) and len(txt_element) >= 2:
                    parsed_result.append({
                        "text": txt_element[0],
                        "conf": float(txt_element[1])
                    })
                elif isinstance(txt_element, (list, tuple)) and len(txt_element) == 1:
                     parsed_result.append({
                        "text": txt_element[0],
                        "conf": 0.0
                    })

        return {"status": "success", "data": parsed_result}

    except Exception as e:
        logger.error(f"PaddleWorker Crash: {e}", exc_info=True)
        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}

if __name__ == "__main__":
    # Simple CLI for testing or if invoked directly via subprocess (though we use multiprocessing)
    pass

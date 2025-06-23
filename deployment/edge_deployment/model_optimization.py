"""
Model Optimization for Edge Deployment
Includes quantization, pruning, and conversion utilities
"""

import torch
import torch.nn as nn
import tensorflow as tf
from tensorflow import lite
import onnx
import onnxruntime
import numpy as np
from pathlib import Path
import json

class ModelOptimizer:
    """Utility class for model optimization and conversion"""
    
    def __init__(self):
        self.supported_formats = ['tflite', 'onnx', 'torchscript', 'tensorrt']
    
    def quantize_tensorflow_model(self, model_path, output_path):
        """Quantize TensorFlow model to TFLite"""
        
        # Load the model
        model = tf.keras.models.load_model(model_path)
        
        # Convert to TFLite with quantization
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        
        # Post-training quantization
        converter.representative_dataset = self._representative_dataset
        converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
        converter.inference_input_type = tf.int8
        converter.inference_output_type = tf.int8
        
        quantized_model = converter.convert()
        
        # Save quantized model
        with open(output_path, 'wb') as f:
            f.write(quantized_model)
        
        print(f"Quantized model saved to {output_path}")
        
        # Compare model sizes
        original_size = Path(model_path).stat().st_size / (1024 * 1024)
        quantized_size = Path(output_path).stat().st_size / (1024 * 1024)
        
        print(f"Original size: {original_size:.2f} MB")
        print(f"Quantized size: {quantized_size:.2f} MB")
        print(f"Compression ratio: {original_size/quantized_size:.2f}x")
        
        return quantized_model
    
    def _representative_dataset(self):
        """Generate representative dataset for quantization"""
        # This should be replaced with actual representative data
        for _ in range(100):
            yield [np.random.random((1, 224, 224, 3)).astype(np.float32)]
    
    def convert_pytorch_to_onnx(self, model, input_shape, output_path):
        """Convert PyTorch model to ONNX format"""
        
        # Set model to evaluation mode
        model.eval()
        
        # Create dummy input
        dummy_input = torch.randn(input_shape)
        
        # Export to ONNX
        torch.onnx.export(
            model,
            dummy_input,
            output_path,
            export_params=True,
            opset_version=11,
            do_constant_folding=True,
            input_names=['input'],
            output_names=['output'],
            dynamic_axes={
                'input': {0: 'batch_size'},
                'output': {0: 'batch_size'}
            }
        )
        
        print(f"ONNX model saved to {output_path}")
        
        # Verify the model
        onnx_model = onnx.load(output_path)
        onnx.checker.check_model(onnx_model)
        print("ONNX model verification passed")
        
        return output_path
    
    def optimize_onnx_model(self, model_path, output_path):
        """Optimize ONNX model for inference"""
        
        import onnxoptimizer
        
        # Load ONNX model
        model = onnx.load(model_path)
        
        # Apply optimizations
        optimized_model = onnxoptimizer.optimize(model)
        
        # Save optimized model
        onnx.save(optimized_model, output_path)
        
        print(f"Optimized ONNX model saved to {output_path}")
        
        return output_path
    
    def convert_to_torchscript(self, model, input_shape, output_path):
        """Convert PyTorch model to TorchScript"""
        
        model.eval()
        
        # Create example input
        example_input = torch.randn(input_shape)
        
        # Trace the model
        traced_model = torch.jit.trace(model, example_input)
        
        # Save traced model
        traced_model.save(output_path)
        
        print(f"TorchScript model saved to {output_path}")
        
        return traced_model
    
    def prune_pytorch_model(self, model, pruning_ratio=0.2):
        """Prune PyTorch model to reduce size"""
        
        import torch.nn.utils.prune as prune
        
        # Apply global magnitude pruning
        parameters_to_prune = []
        for module in model.modules():
            if isinstance(module, (nn.Conv2d, nn.Linear)):
                parameters_to_prune.append((module, 'weight'))
        
        prune.global_unstructured(
            parameters_to_prune,
            pruning_method=prune.L1Unstructured,
            amount=pruning_ratio,
        )
        
        # Remove pruning reparameterization
        for module, param in parameters_to_prune:
            prune.remove(module, param)
        
        print(f"Model pruned with {pruning_ratio*100}% sparsity")
        
        return model
    
    def benchmark_model(self, model_path, model_type='onnx', num_runs=100):
        """Benchmark model inference speed"""
        
        import time
        
        if model_type == 'onnx':
            # Load ONNX model
            session = onnxruntime.InferenceSession(model_path)
            input_name = session.get_inputs()[0].name
            input_shape = session.get_inputs()[0].shape
            
            # Create dummy input
            dummy_input = np.random.randn(*input_shape).astype(np.float32)
            
            # Warm up
            for _ in range(10):
                session.run(None, {input_name: dummy_input})
            
            # Benchmark
            start_time = time.time()
            for _ in range(num_runs):
                session.run(None, {input_name: dummy_input})
            end_time = time.time()
            
        elif model_type == 'tflite':
            # Load TFLite model
            interpreter = tf.lite.Interpreter(model_path=model_path)
            interpreter.allocate_tensors()
            
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            
            # Create dummy input
            input_shape = input_details[0]['shape']
            dummy_input = np.random.randn(*input_shape).astype(np.float32)
            
            # Warm up
            for _ in range(10):
                interpreter.set_tensor(input_details[0]['index'], dummy_input)
                interpreter.invoke()
            
            # Benchmark
            start_time = time.time()
            for _ in range(num_runs):
                interpreter.set_tensor(input_details[0]['index'], dummy_input)
                interpreter.invoke()
            end_time = time.time()
        
        avg_time = (end_time - start_time) / num_runs * 1000  # ms
        fps = 1000 / avg_time
        
        print(f"Average inference time: {avg_time:.2f} ms")
        print(f"Throughput: {fps:.2f} FPS")
        
        return avg_time, fps

class EdgeDeploymentPipeline:
    """Complete pipeline for edge deployment"""
    
    def __init__(self, target_platform='mobile'):
        self.target_platform = target_platform
        self.optimizer = ModelOptimizer()
    
    def prepare_handwriting_model_for_edge(self, model_path, output_dir):
        """Prepare handwriting recognition model for edge deployment"""
        
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        if model_path.endswith('.h5') or model_path.endswith('.keras'):
            # TensorFlow/Keras model
            
            # Convert to TFLite
            tflite_path = output_dir / 'handwriting_model.tflite'
            self.optimizer.quantize_tensorflow_model(model_path, tflite_path)
            
            # Benchmark
            self.optimizer.benchmark_model(tflite_path, 'tflite')
            
        elif model_path.endswith('.pth') or model_path.endswith('.pt'):
            # PyTorch model
            
            # Load model
            model = torch.load(model_path, map_location='cpu')
            model.eval()
            
            # Convert to ONNX
            onnx_path = output_dir / 'handwriting_model.onnx'
            self.optimizer.convert_pytorch_to_onnx(
                model, (1, 1, 64, 256), onnx_path
            )
            
            # Optimize ONNX
            optimized_onnx_path = output_dir / 'handwriting_model_optimized.onnx'
            self.optimizer.optimize_onnx_model(onnx_path, optimized_onnx_path)
            
            # Convert to TorchScript
            torchscript_path = output_dir / 'handwriting_model.pt'
            self.optimizer.convert_to_torchscript(
                model, (1, 1, 64, 256), torchscript_path
            )
            
            # Benchmark
            self.optimizer.benchmark_model(optimized_onnx_path, 'onnx')
        
        # Create deployment config
        config = {
            'model_type': 'handwriting_recognition',
            'input_shape': [1, 64, 256] if 'tamil' in str(model_path) else [3, 224, 224],
            'output_classes': 50,  # Adjust based on vocabulary size
            'preprocessing': {
                'resize': [64, 256],
                'normalize': True,
                'grayscale': True
            },
            'postprocessing': {
                'decode_method': 'greedy',
                'confidence_threshold': 0.5
            }
        }
        
        with open(output_dir / 'config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"Edge deployment files saved to {output_dir}")
    
    def prepare_translation_model_for_edge(self, model_path, output_dir):
        """Prepare translation model for edge deployment"""
        
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        # For translation models, we typically use ONNX or TensorFlow Lite
        if 'pytorch' in str(model_path) or model_path.endswith('.pt'):
            # PyTorch model (mT5)
            
            from transformers import MT5ForConditionalGeneration, MT5Tokenizer
            
            # Load model and tokenizer
            model = MT5ForConditionalGeneration.from_pretrained(model_path)
            tokenizer = MT5Tokenizer.from_pretrained(model_path)
            
            # Convert to ONNX (encoder-decoder models are complex)
            # This is a simplified version - full implementation would handle
            # encoder and decoder separately
            
            print("Translation model optimization for edge deployment")
            print("Note: Full encoder-decoder optimization requires specialized handling")
            
        # Create lightweight business dictionary for offline translation
        business_dict = {
            "நாட்டு சக்கரை": "country sugar",
            "ராகி": "ragi",
            "ராகி மாவு": "ragi flour",
            "கம்பு": "pearl millet",
            "கம்பு மாவு": "pearl millet flour",
            "கொள்ளு": "horse gram",
            "உளுந்து": "black gram",
            "கடலை": "chickpea",
            "பச்சைப் பயறு": "green gram",
            "வாடிக்கையாளர்": "customer",
            "விற்பனை": "sales",
            "கணக்கு": "account",
            "பில்": "bill",
            "தொகை": "amount",
            "கிலோ": "kilogram",
            "விலை": "price",
            "மொத்தம்": "total"
        }
        
        # Add reverse mappings
        reverse_dict = {v: k for k, v in business_dict.items()}
        business_dict.update(reverse_dict)
        
        # Save dictionary for offline use
        with open(output_dir / 'business_dictionary.json', 'w', encoding='utf-8') as f:
            json.dump(business_dict, f, indent=2, ensure_ascii=False)
        
        # Create config
        config = {
            'model_type': 'translation',
            'languages': ['tamil', 'english'],
            'fallback_dictionary': 'business_dictionary.json',
            'max_length': 128,
            'beam_size': 4
        }
        
        with open(output_dir / 'config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"Translation deployment files saved to {output_dir}")
    
    def create_mobile_app_assets(self, models_dir, output_dir):
        """Create assets for mobile app deployment"""
        
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        # Create directory structure for mobile app
        (output_dir / 'models').mkdir(exist_ok=True)
        (output_dir / 'configs').mkdir(exist_ok=True)
        (output_dir / 'dictionaries').mkdir(exist_ok=True)
        
        # Copy optimized models
        models_dir = Path(models_dir)
        
        # Copy TFLite models for Android
        for tflite_file in models_dir.glob('**/*.tflite'):
            import shutil
            shutil.copy(tflite_file, output_dir / 'models' / tflite_file.name)
        
        # Copy Core ML models for iOS (if available)
        for coreml_file in models_dir.glob('**/*.mlmodel'):
            import shutil
            shutil.copy(coreml_file, output_dir / 'models' / coreml_file.name)
        
        # Copy configs and dictionaries
        for config_file in models_dir.glob('**/config.json'):
            import shutil
            shutil.copy(config_file, output_dir / 'configs' / f"{config_file.parent.name}_config.json")
        
        for dict_file in models_dir.glob('**/*dictionary.json'):
            import shutil
            shutil.copy(dict_file, output_dir / 'dictionaries' / dict_file.name)
        
        # Create mobile app manifest
        manifest = {
            'app_name': 'Business Management AI',
            'version': '1.0.0',
            'models': {
                'tamil_handwriting': {
                    'file': 'models/tamil_handwriting.tflite',
                    'config': 'configs/tamil_handwriting_config.json',
                    'type': 'handwriting_recognition'
                },
                'english_handwriting': {
                    'file': 'models/english_handwriting.tflite',
                    'config': 'configs/english_handwriting_config.json',
                    'type': 'handwriting_recognition'
                },
                'invoice_layout': {
                    'file': 'models/invoice_layout.tflite',
                    'config': 'configs/invoice_layout_config.json',
                    'type': 'document_analysis'
                }
            },
            'dictionaries': {
                'business_terms': 'dictionaries/business_dictionary.json'
            },
            'features': [
                'handwriting_recognition',
                'invoice_scanning',
                'offline_translation',
                'sales_analytics'
            ]
        }
        
        with open(output_dir / 'app_manifest.json', 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"Mobile app assets created in {output_dir}")

# Usage example
if __name__ == "__main__":
    # Initialize deployment pipeline
    pipeline = EdgeDeploymentPipeline(target_platform='mobile')
    
    # Prepare models for edge deployment
    # pipeline.prepare_handwriting_model_for_edge(
    #     'models/tamil_handwriting_model.h5',
    #     'deployment/edge/tamil_handwriting'
    # )
    
    # pipeline.prepare_translation_model_for_edge(
    #     'models/tamil_english_translator',
    #     'deployment/edge/translation'
    # )
    
    # Create mobile app assets
    # pipeline.create_mobile_app_assets(
    #     'deployment/edge',
    #     'deployment/mobile_assets'
    # )
    
    print("Edge deployment pipeline ready!")
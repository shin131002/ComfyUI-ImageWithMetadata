# ImageWithMetadata Custom Nodes for ComfyUI
# Based on WAS Node Suite (MIT License)
# https://github.com/WASasquatch/was-node-suite-comfyui

import os
import json
import numpy as np
import torch
from PIL import Image, ImageSequence, ImageOps
from PIL.PngImagePlugin import PngInfo
import folder_paths
from datetime import datetime
import re
import glob


# Counter persistence database (from WAS Node Suite pattern)
class SimpleCounterDB:
    def __init__(self):
        self.db_file = os.path.join(folder_paths.get_temp_directory(), "load_image_counters.json")
        self.data = self.load()
    
    def load(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save(self):
        try:
            with open(self.db_file, 'w') as f:
                json.dump(self.data, f)
        except:
            pass
    
    def get_counter(self, label):
        return self.data.get(f"{label}_counter", 0)
    
    def set_counter(self, label, value):
        self.data[f"{label}_counter"] = value
        self.save()
    
    def get_path(self, label):
        return self.data.get(f"{label}_path", "")
    
    def set_path(self, label, value):
        self.data[f"{label}_path"] = value
        self.save()
    
    def get_pattern(self, label):
        return self.data.get(f"{label}_pattern", "*")
    
    def set_pattern(self, label, value):
        self.data[f"{label}_pattern"] = value
        self.save()


counter_db = SimpleCounterDB()


class SaveImageWithMetadata:
    """Save images with generation metadata to PNG/WebP/JPG and optional text files"""
    
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "positive_prompt": ("STRING", {"multiline": True}),
                "negative_prompt": ("STRING", {"multiline": True}),
                "filename_prefix": ("STRING", {"default": "%date:yyMM%/%date:yyMMdd-hhmmss%"}),
                "image_format": (["png", "webp", "jpg"],),
                "metadata_save": (["png_metadata_only", "text_file_only", "both"],),
                "text_format": (["json", "plain_text"],),
            },
            "optional": {
                "model_name": ("STRING", {"default": ""}),
                "vae_name": ("STRING", {"default": ""}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff, "forceInput": True}),
                "sampler_name": ("*", {"forceInput": True}),
                "scheduler": ("*", {"forceInput": True}),
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                "cfg": ("FLOAT", {"default": 7.0, "min": 0.0, "max": 100.0}),
                "memo": ("STRING", {"multiline": True, "default": ""}),
                "save_model": ("BOOLEAN", {"default": True}),
                "save_vae": ("BOOLEAN", {"default": True}),
                "save_seed": ("BOOLEAN", {"default": True}),
                "save_sampler": ("BOOLEAN", {"default": True}),
                "save_scheduler": ("BOOLEAN", {"default": True}),
                "save_steps": ("BOOLEAN", {"default": True}),
                "save_cfg": ("BOOLEAN", {"default": True}),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = ()
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "image"

    def save_images(self, images, positive_prompt, negative_prompt, filename_prefix, 
                    image_format, metadata_save, text_format,
                    model_name="", vae_name="", seed=0, sampler_name=None, scheduler=None, steps=20, cfg=7.0, memo="",
                    save_model=True, save_vae=True, save_seed=True, save_sampler=True, 
                    save_scheduler=True, save_steps=True, save_cfg=True,
                    prompt=None, extra_pnginfo=None):
        
        # Process filename prefix (date format)
        filename_prefix = self.process_filename_prefix(filename_prefix)
        
        # Create output directory
        full_output_folder, filename, counter, subfolder, filename_prefix = \
            folder_paths.get_save_image_path(filename_prefix, self.output_dir, 
                                            images[0].shape[1], images[0].shape[0])
        
        results = list()
        
        # Prepare metadata
        metadata_dict = self.prepare_metadata(
            positive_prompt, negative_prompt, model_name, vae_name, seed, sampler_name, 
            scheduler, steps, cfg, memo, save_model, save_vae, save_seed, save_sampler, 
            save_scheduler, save_steps, save_cfg
        )
        
        for image in images:
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            
            # Generate filename
            file = f"{filename}_{counter:05d}_.{image_format}"
            
            # Prepare PNG metadata
            metadata = None
            if image_format == "png":
                metadata = PngInfo()
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))
                
                # Add custom metadata
                if metadata_save in ["png_metadata_only", "both"]:
                    metadata.add_text("user_metadata", json.dumps(metadata_dict))
            
            # Save image
            img_path = os.path.join(full_output_folder, file)
            if image_format == "png":
                img.save(img_path, pnginfo=metadata, compress_level=self.compress_level)
            elif image_format == "webp":
                img.save(img_path, quality=95)
            elif image_format == "jpg":
                img.save(img_path, quality=95)
            
            # Save text file
            if metadata_save in ["text_file_only", "both"]:
                text_file = f"{filename}_{counter:05d}_.txt"
                text_path = os.path.join(full_output_folder, text_file)
                
                if text_format == "json":
                    with open(text_path, 'w', encoding='utf-8') as f:
                        json.dump(metadata_dict, f, ensure_ascii=False, indent=2)
                else:  # plain_text
                    with open(text_path, 'w', encoding='utf-8') as f:
                        f.write(self.format_plain_text(metadata_dict))
            
            results.append({
                "filename": file,
                "subfolder": subfolder,
                "type": self.type
            })
            counter += 1
        
        return {"ui": {"images": results}}

    def process_filename_prefix(self, prefix):
        """Process date format in filename prefix"""
        now = datetime.now()
        
        # Detect and replace %date:format%
        def replace_date(match):
            date_format = match.group(1)
            # Convert to strftime format
            date_format = date_format.replace('yy', '%y').replace('MM', '%m').replace('dd', '%d')
            date_format = date_format.replace('hh', '%H').replace('mm', '%M').replace('ss', '%S')
            return now.strftime(date_format)
        
        prefix = re.sub(r'%date:([^%]+)%', replace_date, prefix)
        return prefix

    def prepare_metadata(self, positive_prompt, negative_prompt, model_name, vae_name, seed, 
                        sampler_name, scheduler, steps, cfg, memo, save_model, save_vae, 
                        save_seed, save_sampler, save_scheduler, save_steps, save_cfg):
        """Prepare metadata dictionary"""
        metadata = {
            "positive_prompt": positive_prompt,
            "negative_prompt": negative_prompt,
        }
        
        if save_model and model_name:
            metadata["model"] = model_name
        
        if save_vae and vae_name:
            metadata["vae"] = vae_name
        
        if save_seed:
            metadata["seed"] = seed
        
        if save_sampler and sampler_name is not None:
            metadata["sampler_name"] = str(sampler_name)
        
        if save_scheduler and scheduler is not None:
            metadata["scheduler"] = str(scheduler)
        
        if save_steps:
            metadata["steps"] = steps
        
        if save_cfg:
            metadata["cfg"] = cfg
        
        if memo:
            metadata["memo"] = memo
        
        return metadata

    def format_plain_text(self, metadata):
        """Format metadata as plain text"""
        lines = []
        
        if "model" in metadata:
            lines.append(f"Model: {metadata['model']}")
        if "vae" in metadata:
            lines.append(f"VAE: {metadata['vae']}")
        if "seed" in metadata:
            lines.append(f"Seed: {metadata['seed']}")
        if "sampler_name" in metadata:
            lines.append(f"Sampler: {metadata['sampler_name']}")
        if "scheduler" in metadata:
            lines.append(f"Scheduler: {metadata['scheduler']}")
        if "steps" in metadata:
            lines.append(f"Steps: {metadata['steps']}")
        if "cfg" in metadata:
            lines.append(f"CFG: {metadata['cfg']}")
        
        lines.append("Positive: =======================================")
        lines.append(metadata["positive_prompt"])
        
        lines.append("Negative: =======================================")
        lines.append(metadata["negative_prompt"])
        
        if "memo" in metadata and metadata["memo"]:
            lines.append("Memo: =======================================")
            lines.append(metadata["memo"])
        
        return "\n".join(lines)


class LoadImageWithMetadata:
    """
    Load images from folder with metadata output
    Based on WAS Node Suite's Load_Image_Batch with metadata extraction
    """
    
    def __init__(self):
        self.HDB = counter_db
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mode": (["single_image", "incremental_image"],),
                "path": ("STRING", {"default": "", "multiline": False}),
                "pattern": ("STRING", {"default": "*", "multiline": False}),
                "label": ("STRING", {"default": "Batch 001", "multiline": False}),
                "index": ("INT", {"default": 0, "min": 0, "max": 150000, "step": 1}),
            },
            "optional": {
                "filename_text_extension": (["true", "false"],),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING", "STRING", "STRING", "STRING", "INT", "INT", "FLOAT")
    RETURN_NAMES = ("image", "positive_prompt", "negative_prompt", "info", "filename_text", "seed", "steps", "cfg")
    FUNCTION = "load_batch_images"
    CATEGORY = "image"
    
    def load_batch_images(self, mode, path, pattern, label, index, filename_text_extension="true"):
        # Use default input directory if path is empty
        if not path or path.strip() == "":
            path = folder_paths.get_input_directory()
        
        if not os.path.exists(path):
            # Return empty data on error
            return (torch.zeros((1, 64, 64, 3)), "", "", "", "", 0, 20, 7.0)
        
        # Use BatchImageLoader
        fl = self.BatchImageLoader(path, label, pattern)
        
        if not fl.image_paths:
            return (torch.zeros((1, 64, 64, 3)), "", "", "", "", 0, 20, 7.0)
        
        # Get image based on mode
        if mode == "single_image":
            # single_image mode: use index (with wrap-around)
            index = index % len(fl.image_paths)  # Ensure index is within range
            image, filename, image_path = fl.get_image_by_id(index)
            if image is None:
                return (torch.zeros((1, 64, 64, 3)), "", "", "", "", 0, 20, 7.0)
        elif mode == "incremental_image":
            # incremental_image mode: use counter (index is ignored)
            image, filename, image_path = fl.get_next_image()
            if image is None:
                return (torch.zeros((1, 64, 64, 3)), "", "", "", "", 0, 20, 7.0)
        else:
            index = index % len(fl.image_paths)  # Ensure index is within range
            image, filename, image_path = fl.get_image_by_id(index)
            if image is None:
                return (torch.zeros((1, 64, 64, 3)), "", "", "", "", 0, 20, 7.0)
        
        # Convert to RGB
        image = image.convert("RGB")
        
        # Process filename
        if filename_text_extension == "false":
            filename = os.path.splitext(filename)[0]
        
        # PIL to tensor (WAS method)
        image_tensor = torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)
        
        # Load metadata
        metadata = self.load_metadata(image_path)
        
        # Generate info string
        info_lines = []
        if "model" in metadata and metadata["model"]:
            info_lines.append(f"MODEL: {metadata['model']}")
        if "vae" in metadata and metadata["vae"]:
            info_lines.append(f"VAE: {metadata['vae']}")
        if "sampler_name" in metadata and metadata["sampler_name"]:
            info_lines.append(f"Sampler: {metadata['sampler_name']}")
        if "scheduler" in metadata and metadata["scheduler"]:
            info_lines.append(f"Scheduler: {metadata['scheduler']}")
        
        info_text = "\n".join(info_lines) if info_lines else ""
        
        return (
            image_tensor,
            metadata.get("positive_prompt", ""),
            metadata.get("negative_prompt", ""),
            info_text,
            filename,
            metadata.get("seed", 0),
            metadata.get("steps", 20),
            metadata.get("cfg", 7.0)
        )
    
    class BatchImageLoader:
        """
        Batch image loader (WAS Node Suite pattern)
        Manages image list and counter persistence
        """
        
        def __init__(self, directory_path, label, pattern):
            self.DB = counter_db
            self.image_paths = []
            self.load_images(directory_path, pattern)
            self.image_paths.sort()
            
            # Counter management (WAS method)
            stored_directory_path = self.DB.get_path(label)
            stored_pattern = self.DB.get_pattern(label)
            
            if stored_directory_path != directory_path or stored_pattern != pattern:
                self.index = 0
                self.DB.set_counter(label, 0)
                self.DB.set_path(label, directory_path)
                self.DB.set_pattern(label, pattern)
            else:
                self.index = self.DB.get_counter(label)
            
            self.label = label
        
        def load_images(self, directory_path, pattern):
            """Load image file list (WAS method)"""
            allowed_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif')
            
            for file_name in glob.glob(os.path.join(glob.escape(directory_path), pattern), recursive=True):
                if file_name.lower().endswith(allowed_extensions):
                    abs_file_path = os.path.abspath(file_name)
                    self.image_paths.append(abs_file_path)
        
        def get_image_by_id(self, image_id):
            """Get image by ID (WAS method)"""
            if image_id < 0 or image_id >= len(self.image_paths):
                print(f"Invalid image index `{image_id}`")
                return (None, None, None)
            
            image_path = self.image_paths[image_id]
            i = Image.open(image_path)
            i = ImageOps.exif_transpose(i)
            return (i, os.path.basename(image_path), image_path)
        
        def get_next_image(self):
            """Get next image and increment counter (WAS method)"""
            if self.index >= len(self.image_paths):
                self.index = 0
            
            image_path = self.image_paths[self.index]
            self.index += 1
            
            if self.index == len(self.image_paths):
                self.index = 0
            
            # Save counter
            self.DB.set_counter(self.label, self.index)
            
            i = Image.open(image_path)
            i = ImageOps.exif_transpose(i)
            return (i, os.path.basename(image_path), image_path)
    
    def load_metadata(self, image_path):
        """Load metadata from image or text file"""
        metadata = {}
        
        # Try PNG metadata first
        if image_path.lower().endswith('.png'):
            try:
                img = Image.open(image_path)
                if 'user_metadata' in img.info:
                    # Our custom format
                    try:
                        metadata = json.loads(img.info['user_metadata'])
                        return metadata
                    except:
                        pass
                elif 'parameters' in img.info:
                    # A1111 format
                    try:
                        params = img.info['parameters']
                        metadata = self.parse_a1111_metadata(params)
                        return metadata
                    except:
                        pass
            except:
                pass
        
        # Try text file
        text_path = os.path.splitext(image_path)[0] + '.txt'
        if os.path.exists(text_path):
            try:
                with open(text_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Try JSON format
                if content.strip().startswith('{'):
                    try:
                        metadata = json.loads(content)
                        return metadata
                    except:
                        pass
                else:
                    # Try plain text format
                    metadata = self.parse_plain_text_metadata(content)
                    return metadata
            except:
                pass
        
        return metadata
    
    def parse_a1111_metadata(self, params_text):
        """Parse A1111 format metadata"""
        metadata = {}
        
        # Basic parsing (can be enhanced)
        lines = params_text.split('\n')
        if len(lines) >= 2:
            metadata['positive_prompt'] = lines[0]
            
            # Parse parameters line
            if 'Negative prompt:' in params_text:
                parts = params_text.split('Negative prompt:')
                metadata['positive_prompt'] = parts[0].strip()
                remaining = parts[1]
                
                if '\n' in remaining:
                    neg_parts = remaining.split('\n', 1)
                    metadata['negative_prompt'] = neg_parts[0].strip()
                    
                    # Parse other parameters
                    if len(neg_parts) > 1:
                        param_line = neg_parts[1]
                        metadata.update(self.parse_parameter_line(param_line))
        
        return metadata
    
    def parse_parameter_line(self, param_line):
        """Parse parameter line (Steps: 20, Sampler: ..., etc.)"""
        params = {}
        
        # Simple regex parsing
        import re
        
        seed_match = re.search(r'Seed:\s*(\d+)', param_line)
        if seed_match:
            params['seed'] = int(seed_match.group(1))
        
        steps_match = re.search(r'Steps:\s*(\d+)', param_line)
        if steps_match:
            params['steps'] = int(steps_match.group(1))
        
        cfg_match = re.search(r'CFG scale:\s*([\d.]+)', param_line)
        if cfg_match:
            params['cfg'] = float(cfg_match.group(1))
        
        sampler_match = re.search(r'Sampler:\s*([^,]+)', param_line)
        if sampler_match:
            params['sampler_name'] = sampler_match.group(1).strip()
        
        return params
    
    def parse_plain_text_metadata(self, content):
        """Parse plain text format metadata"""
        metadata = {}
        lines = content.split('\n')
        
        current_section = None
        section_content = []
        
        for line in lines:
            if line.startswith('Model:'):
                metadata['model'] = line.replace('Model:', '').strip()
            elif line.startswith('VAE:'):
                metadata['vae'] = line.replace('VAE:', '').strip()
            elif line.startswith('Seed:'):
                try:
                    metadata['seed'] = int(line.replace('Seed:', '').strip())
                except:
                    pass
            elif line.startswith('Sampler:'):
                metadata['sampler_name'] = line.replace('Sampler:', '').strip()
            elif line.startswith('Scheduler:'):
                metadata['scheduler'] = line.replace('Scheduler:', '').strip()
            elif line.startswith('Steps:'):
                try:
                    metadata['steps'] = int(line.replace('Steps:', '').strip())
                except:
                    pass
            elif line.startswith('CFG:'):
                try:
                    metadata['cfg'] = float(line.replace('CFG:', '').strip())
                except:
                    pass
            elif 'Positive:' in line:
                if current_section and section_content:
                    metadata[current_section] = '\n'.join(section_content).strip()
                current_section = 'positive_prompt'
                section_content = []
            elif 'Negative:' in line:
                if current_section and section_content:
                    metadata[current_section] = '\n'.join(section_content).strip()
                current_section = 'negative_prompt'
                section_content = []
            elif 'Memo:' in line:
                if current_section and section_content:
                    metadata[current_section] = '\n'.join(section_content).strip()
                current_section = 'memo'
                section_content = []
            elif current_section:
                section_content.append(line)
        
        # Add last section
        if current_section and section_content:
            metadata[current_section] = '\n'.join(section_content).strip()
        
        return metadata


class CheckpointLoaderWithNames:
    """
    Checkpoint loader that returns model and VAE names as strings
    Useful for connecting to SaveImageWithMetadata
    """
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "ckpt_name": (folder_paths.get_filename_list("checkpoints"),),
            },
            "optional": {
                "vae_name": (["Baked VAE"] + folder_paths.get_filename_list("vae"),),
            }
        }
    
    RETURN_TYPES = ("MODEL", "CLIP", "VAE", "STRING", "STRING")
    RETURN_NAMES = ("model", "clip", "vae", "checkpoint_name", "vae_name")
    FUNCTION = "load_checkpoint"
    CATEGORY = "loaders"

    def load_checkpoint(self, ckpt_name, vae_name="Baked VAE"):
        # Load checkpoint
        from nodes import CheckpointLoaderSimple, VAELoader
        loader = CheckpointLoaderSimple()
        model, clip, vae = loader.load_checkpoint(ckpt_name)
        
        actual_vae_name = ""
        
        # VAE processing
        if vae_name == "Baked VAE":
            # Use baked VAE from checkpoint
            actual_vae_name = f"{ckpt_name} (Baked VAE)"
        else:
            # Load external VAE
            vae_loader = VAELoader()
            vae = vae_loader.load_vae(vae_name)[0]
            actual_vae_name = vae_name
        
        return (model, clip, vae, ckpt_name, actual_vae_name)


# Node mappings
NODE_CLASS_MAPPINGS = {
    "SaveImageWithMetadata": SaveImageWithMetadata,
    "LoadImageWithMetadata": LoadImageWithMetadata,
    "CheckpointLoaderWithNames": CheckpointLoaderWithNames,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveImageWithMetadata": "Save Image with Metadata",
    "LoadImageWithMetadata": "Load Image with Metadata",
    "CheckpointLoaderWithNames": "Checkpoint Loader with Names",
}

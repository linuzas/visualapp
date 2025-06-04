# api/content_agent.py
import os
import base64
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI

class ContentAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    
    def classify_images(self, image_data_list: List[Dict]) -> List[str]:
        """Classify images as product, avatar, or other"""
        descriptions = []
        
        for img_data in image_data_list:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4-vision-preview",
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "What is this image? Reply with only: 'product', 'avatar', or 'other'."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_data['base64']}"}}
                        ]
                    }],
                    max_tokens=10
                )
                descriptions.append(response.choices[0].message.content.strip().lower())
            except Exception as e:
                print(f"Classification error: {e}")
                descriptions.append("other")
        
        return descriptions
    
    def scan_products(self, image_data_list: List[Dict], descriptions: List[str]) -> List[Dict]:
        """Scan products from images"""
        products = []
        
        for img_data, desc in zip(image_data_list, descriptions):
            if desc != "product":
                continue
            
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4-vision-preview",
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": 'Identify the product. Return JSON: {"product_name": "name", "product_type": "type", "brand_name": "brand or null"}'},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_data['base64']}"}}
                        ]
                    }],
                    max_tokens=100
                )
                
                content = response.choices[0].message.content.strip()
                # Extract JSON from response
                start = content.find('{')
                end = content.rfind('}') + 1
                if start >= 0 and end > start:
                    json_str = content[start:end]
                    data = json.loads(json_str)
                    products.append(data)
            except Exception as e:
                print(f"Product scan error: {e}")
        
        return products
    
    def generate_prompts(self, products: List[Dict], has_avatar: bool) -> List[str]:
        """Generate simplified prompts"""
        prompts = []
        
        for product in products:
            name = product.get("product_name", "product")
            ptype = product.get("product_type", "item")
            
            if has_avatar:
                # Avatar + product prompt
                prompts.extend([
                    f"8K cinematic shot of a happy person using {name} ({ptype}), golden hour lighting, shallow depth-of-field, lifestyle photography",
                    f"Professional advertisement photo: confident person showcasing {name}, studio lighting, modern aesthetic",
                    f"Lifestyle moment: person enjoying {name} in everyday setting, natural lighting, authentic emotion"
                ])
            else:
                # Product only prompts
                prompts.extend([
                    f"8K product photography of {name} ({ptype}), studio lighting, minimalist white background, professional commercial shot",
                    f"Hero shot of {name}, dramatic lighting, premium product presentation, luxury aesthetic",
                    f"Creative product display: {name} with complementary props, artistic composition, magazine-style photography"
                ])
        
        return prompts[:3]  # Limit to 3 prompts
    
    def process(self, image_data_list: List[Dict]) -> Dict:
        """Main processing pipeline"""
        try:
            # 1. Classify images
            descriptions = self.classify_images(image_data_list)
            
            # 2. Check validity
            has_products = "product" in descriptions
            has_avatar = "avatar" in descriptions
            
            if not has_products:
                return {
                    "success": False,
                    "error": "No products detected in images. Please upload clear product photos.",
                    "descriptions": descriptions
                }
            
            # 3. Scan products
            products = self.scan_products(image_data_list, descriptions)
            
            if not products:
                return {
                    "success": False,
                    "error": "Could not identify products in the images.",
                    "descriptions": descriptions
                }
            
            # 4. Generate prompts
            prompts = self.generate_prompts(products, has_avatar)
            
            return {
                "success": True,
                "descriptions": descriptions,
                "products": products,
                "prompts": prompts,
                "has_avatar": has_avatar,
                "message": f"Successfully processed {len(products)} product(s)" + (" with avatar" if has_avatar else "")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Processing failed: {str(e)}"
            }

# Singleton instance
agent = ContentAgent() 

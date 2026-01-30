"""
Gemini AI Grading Utility for Waste Quality Assessment
"""
import google.generativeai as genai
from PIL import Image
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')




def audit_waste_images(image_paths):
    """
    Analyze waste images using Gemini AI and return quality grading
    
    Args:
        image_paths: List of file paths to images (up to 5)
    
    Returns:
        dict: Grading result with material, grade, confidence, and notes
    """
    try:
        # Load all images
        images = []
        for path in image_paths:
            if path:
                try:
                    img = Image.open(path)
                    images.append(img)
                except Exception as e:
                    logger.warning(f"Could not load image {path}: {e}")
                    continue
        
        if not images:
            return {
                "material": "Unknown",
                "grade": "C",
                "confidence": 0.0,
                "audit_notes": "No valid images provided"
            }
        
        # Define the grading prompt
        prompt = """
        You are an industrial waste quality auditor. Analyze these images of a waste batch.
        
        Grading Criteria:
        - Grade A: Clean, no contamination, high resale value (e.g., clear dry plastic, pure metal).
        - Grade B: Slight contamination or mixed materials (e.g., some labels, dust, or minor food residue).
        - Grade C: Highly contaminated or hazardous (e.g., muddy, oily, mixed with organic rot).
        
        Identify the material type and provide a final Grade based on the consistency across all photos.
        
        Output format (JSON only, no markdown):
        {
          "material": "Type of waste",
          "grade": "A, B, or C",
          "confidence": 0.95,
          "audit_notes": "Brief reason for the grade"
        }
        """
        
        # Generate content
        response = model.generate_content([prompt, *images])
        
        # Parse response
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Parse JSON
        result = json.loads(response_text)
        
        # Validate structure
        required_keys = ["material", "grade", "confidence", "audit_notes"]
        for key in required_keys:
            if key not in result:
                raise ValueError(f"Missing required key: {key}")
        
        # Normalize grade to uppercase
        result['grade'] = result['grade'].upper()
        if result['grade'] not in ['A', 'B', 'C']:
            result['grade'] = 'B'  # Default to B if invalid
        
        logger.info(f"Gemini grading successful: {result}")
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {e}")
        logger.error(f"Response text: {response.text if 'response' in locals() else 'N/A'}")
        return {
            "material": "Unknown",
            "grade": "B",
            "confidence": 0.5,
            "audit_notes": f"AI response parsing failed: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return {
            "material": "Unknown",
            "grade": "B",
            "confidence": 0.5,
            "audit_notes": f"Grading failed: {str(e)}"
        }


def apply_gemini_grading(listing):
    """
    Apply Gemini AI grading to a waste listing
    
    Args:
        listing: WasteListing instance
    
    Returns:
        dict: Grading result
    """
    print(f"\n🔍 Starting Gemini grading for listing: {listing.title}")
    
    # Collect image paths
    image_paths = []
    for img_field in [listing.image1, listing.image2, listing.image3, listing.image4, listing.image5]:
        if img_field:
            image_paths.append(img_field.path)
            print(f"  📸 Added image: {img_field.name}")
    
    if not image_paths:
        print("  ⚠️  No images uploaded")
        return {
            "material": listing.material.name,
            "grade": "C",
            "confidence": 0.0,
            "audit_notes": "No images uploaded"
        }
    
    print(f"  📊 Total images for analysis: {len(image_paths)}")
    
    # Get Gemini grading
    print("  🤖 Calling Gemini API...")
    grading_result = audit_waste_images(image_paths)
    
    # Update listing with grading
    listing.gemini_grading_result = grading_result
    listing.grade = grading_result['grade']
    listing.verification_notes = f"Gemini AI: {grading_result['audit_notes']}"
    
    # Set trust score based on confidence
    confidence = float(grading_result.get('confidence', 0.5))
    listing.trust_score = int(confidence * 100)
    
    print(f"  ✅ Grading applied: Grade {listing.grade}, Trust {listing.trust_score}%")
    print(f"  💾 Saving listing...")
    
    listing.save()
    
    print(f"  🎉 Gemini grading complete!\n")
    return grading_result

"""
Professional Mock Data Generator for Social Media
Provides realistic, brand-specific social media data patterns
"""

import random
import hashlib
from typing import Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger

class SocialMediaMockGenerator:
    """Generate realistic social media data based on brand characteristics"""
    
    def __init__(self):
        # Industry-specific base metrics
        self.industry_profiles = {
            'technology': {
                'sentiment_range': (0.65, 0.85),
                'engagement_base': 0.035,
                'mentions_multiplier': 1.2,
                'topics': ['innovation', 'digital transformation', 'AI', 'cloud', 'security']
            },
            'finance': {
                'sentiment_range': (0.55, 0.75),
                'engagement_base': 0.025,
                'mentions_multiplier': 1.0,
                'topics': ['banking', 'investment', 'fintech', 'security', 'customer service']
            },
            'healthcare': {
                'sentiment_range': (0.70, 0.90),
                'engagement_base': 0.040,
                'mentions_multiplier': 0.8,
                'topics': ['patient care', 'innovation', 'health', 'research', 'community']
            },
            'retail': {
                'sentiment_range': (0.60, 0.80),
                'engagement_base': 0.045,
                'mentions_multiplier': 1.5,
                'topics': ['customer experience', 'shopping', 'deals', 'quality', 'service']
            },
            'consulting': {
                'sentiment_range': (0.65, 0.82),
                'engagement_base': 0.030,
                'mentions_multiplier': 0.9,
                'topics': ['expertise', 'transformation', 'solutions', 'consulting', 'leadership']
            },
            'default': {
                'sentiment_range': (0.60, 0.80),
                'engagement_base': 0.035,
                'mentions_multiplier': 1.0,
                'topics': ['business', 'service', 'quality', 'innovation', 'customer']
            }
        }
        
        # Brand size categories (based on name hash)
        self.brand_sizes = {
            'enterprise': {'follower_base': 50000, 'mentions_base': 500, 'posts_base': 20},
            'large': {'follower_base': 25000, 'mentions_base': 300, 'posts_base': 15},
            'medium': {'follower_base': 10000, 'mentions_base': 150, 'posts_base': 10},
            'small': {'follower_base': 5000, 'mentions_base': 80, 'posts_base': 5}
        }
        
        # Realistic post templates
        self.post_templates = {
            'positive': [
                "Great experience with {brand}! Their {service} really impressed me.",
                "Just had excellent customer service from {brand}. Highly recommend!",
                "{brand} continues to innovate and deliver quality results.",
                "Love working with {brand} - they truly understand our needs.",
                "Another successful project completed with {brand}. Thank you!"
            ],
            'neutral': [
                "{brand} announced their new {service} initiative today.",
                "Attending the {brand} webinar on {topic}. Interesting insights.",
                "{brand} has been in the news recently for their {topic} work.",
                "Looking forward to seeing {brand}'s presentation next week.",
                "Checking out {brand}'s latest {service} offering."
            ],
            'negative': [
                "Had some issues with {brand}'s {service} recently. Hope they improve.",
                "Waiting for {brand} to resolve the {service} problem we reported.",
                "{brand} needs to work on their customer communication.",
                "Expected better from {brand} given their reputation.",
                "Service from {brand} was below expectations this time."
            ]
        }
    
    def _get_brand_hash(self, brand_name: str) -> int:
        """Generate consistent hash for brand-specific data"""
        return int(hashlib.md5(brand_name.lower().encode()).hexdigest()[:8], 16)
    
    def _detect_industry(self, brand_name: str) -> str:
        """Detect industry based on brand name patterns"""
        brand_lower = brand_name.lower()
        
        tech_keywords = ['tech', 'soft', 'data', 'cloud', 'digital', 'ai', 'cyber', 'intel', 'microsoft', 'google', 'amazon', 'meta', 'tesla']
        finance_keywords = ['bank', 'financial', 'capital', 'invest', 'credit', 'insurance', 'goldman', 'morgan', 'wells', 'chase']
        healthcare_keywords = ['health', 'medical', 'pharma', 'care', 'hospital', 'clinic', 'pfizer', 'johnson']
        retail_keywords = ['retail', 'store', 'shop', 'mart', 'target', 'walmart', 'amazon', 'costco']
        consulting_keywords = ['consult', 'advisory', 'solutions', 'services', 'accenture', 'deloitte', 'mckinsey', 'pwc', 'ey', 'kpmg', 'cognizant', 'tcs', 'wipro', 'infosys']
        
        for keyword in tech_keywords:
            if keyword in brand_lower:
                return 'technology'
        
        for keyword in finance_keywords:
            if keyword in brand_lower:
                return 'finance'
        
        for keyword in healthcare_keywords:
            if keyword in brand_lower:
                return 'healthcare'
        
        for keyword in retail_keywords:
            if keyword in brand_lower:
                return 'retail'
        
        for keyword in consulting_keywords:
            if keyword in brand_lower:
                return 'consulting'
        
        return 'default'
    
    def _get_brand_size(self, brand_hash: int) -> str:
        """Determine brand size category"""
        size_value = brand_hash % 100
        
        if size_value < 10:  # 10% are enterprise
            return 'enterprise'
        elif size_value < 30:  # 20% are large
            return 'large'
        elif size_value < 70:  # 40% are medium
            return 'medium'
        else:  # 30% are small
            return 'small'
    
    def generate_facebook_data(self, brand_name: str, area_id: str = None) -> Dict[str, Any]:
        """Generate realistic Facebook data for a brand"""
        
        brand_hash = self._get_brand_hash(brand_name)
        industry = self._detect_industry(brand_name)
        brand_size = self._get_brand_size(brand_hash)
        
        profile = self.industry_profiles[industry]
        size_data = self.brand_sizes[brand_size]
        
        # Calculate metrics with some randomness but consistency
        random.seed(brand_hash)  # Consistent randomness for same brand
        
        sentiment_min, sentiment_max = profile['sentiment_range']
        base_sentiment = sentiment_min + (sentiment_max - sentiment_min) * (brand_hash % 100) / 100
        sentiment = round(base_sentiment + random.uniform(-0.05, 0.05), 3)
        
        mentions = int(size_data['mentions_base'] * profile['mentions_multiplier'] * (0.8 + 0.4 * random.random()))
        followers = int(size_data['follower_base'] * (0.7 + 0.6 * random.random()))
        engagement_rate = round(profile['engagement_base'] * (0.8 + 0.4 * random.random()), 4)
        
        # Generate posts
        posts = self._generate_posts(brand_name, profile['topics'], size_data['posts_base'], sentiment)
        
        logger.info(f"Generated Facebook mock data for {brand_name} (Industry: {industry}, Size: {brand_size})")
        
        return {
            "sentiment": sentiment,
            "mentions": mentions,
            "followers": followers,
            "engagement_rate": engagement_rate,
            "posts": posts,
            "platform_specific": {
                "page_likes": followers,
                "check_ins": random.randint(100, 1000),
                "about": f"{brand_name} - Leading {industry} company providing innovative solutions.",
                "website": f"https://www.{brand_name.lower().replace(' ', '')}.com"
            },
            "raw_data": {
                "title": f"{brand_name} - Facebook Page",
                "description": f"Official Facebook page of {brand_name}",
                "industry": industry,
                "brand_size": brand_size
            }
        }
    
    def generate_linkedin_data(self, brand_name: str, area_id: str = None) -> Dict[str, Any]:
        """Generate realistic LinkedIn data for a brand"""
        
        brand_hash = self._get_brand_hash(brand_name)
        industry = self._detect_industry(brand_name)
        brand_size = self._get_brand_size(brand_hash)
        
        profile = self.industry_profiles[industry]
        size_data = self.brand_sizes[brand_size]
        
        # LinkedIn typically has higher engagement and more professional sentiment
        random.seed(brand_hash + 1)  # Different seed for different platform
        
        sentiment_min, sentiment_max = profile['sentiment_range']
        base_sentiment = sentiment_min + (sentiment_max - sentiment_min) * (brand_hash % 100) / 100
        sentiment = round(min(0.95, base_sentiment + 0.1), 3)  # LinkedIn generally more positive
        
        mentions = int(size_data['mentions_base'] * 0.6 * profile['mentions_multiplier'])  # LinkedIn has fewer but higher quality mentions
        followers = int(size_data['follower_base'] * 1.2)  # Companies often have more LinkedIn followers
        engagement_rate = round(profile['engagement_base'] * 1.3, 4)  # Higher engagement on LinkedIn
        
        # Generate professional posts
        posts = self._generate_linkedin_posts(brand_name, profile['topics'], size_data['posts_base'], sentiment)
        
        # Employee count estimation
        employee_ranges = {
            'enterprise': random.randint(10000, 100000),
            'large': random.randint(1000, 10000),
            'medium': random.randint(200, 1000),
            'small': random.randint(50, 200)
        }
        
        logger.info(f"Generated LinkedIn mock data for {brand_name} (Industry: {industry}, Size: {brand_size})")
        
        return {
            "sentiment": sentiment,
            "mentions": mentions,
            "followers": followers,
            "engagement_rate": engagement_rate,
            "posts": posts,
            "platform_specific": {
                "company_size": employee_ranges[brand_size],
                "industry": industry.title(),
                "headquarters": "Global",
                "specialties": profile['topics'][:3],
                "founded": random.randint(1980, 2010)
            },
            "raw_data": {
                "title": f"{brand_name} | LinkedIn",
                "company_info": f"{brand_name} is a {industry} company specializing in {', '.join(profile['topics'][:3])}.",
                "industry": industry,
                "brand_size": brand_size
            }
        }
    
    def _generate_posts(self, brand_name: str, topics: List[str], post_count: int, overall_sentiment: float) -> List[Dict[str, Any]]:
        """Generate realistic social media posts"""
        posts = []
        
        # Sentiment distribution based on overall sentiment
        positive_ratio = max(0.3, overall_sentiment - 0.1)
        negative_ratio = max(0.1, 0.9 - overall_sentiment)
        neutral_ratio = 1.0 - positive_ratio - negative_ratio
        
        for i in range(post_count):
            # Determine post sentiment
            rand_val = random.random()
            if rand_val < positive_ratio:
                post_type = 'positive'
                post_sentiment = random.uniform(0.7, 1.0)
            elif rand_val < positive_ratio + neutral_ratio:
                post_type = 'neutral'
                post_sentiment = random.uniform(0.4, 0.6)
            else:
                post_type = 'negative'
                post_sentiment = random.uniform(0.0, 0.3)
            
            # Select template and customize
            template = random.choice(self.post_templates[post_type])
            service = random.choice(['service', 'solution', 'platform', 'technology', 'offering'])
            topic = random.choice(topics)
            
            post_text = template.format(
                brand=brand_name,
                service=service,
                topic=topic
            )
            
            # Generate engagement metrics
            base_engagement = random.randint(5, 50)
            if post_type == 'positive':
                base_engagement *= random.uniform(1.5, 3.0)
            elif post_type == 'negative':
                base_engagement *= random.uniform(0.3, 0.8)
            
            posts.append({
                "text": post_text,
                "sentiment": round(post_sentiment, 3),
                "engagement": int(base_engagement),
                "likes": int(base_engagement * 0.7),
                "shares": int(base_engagement * 0.2),
                "comments": int(base_engagement * 0.1),
                "date": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                "type": post_type
            })
        
        return posts
    
    def _generate_linkedin_posts(self, brand_name: str, topics: List[str], post_count: int, overall_sentiment: float) -> List[Dict[str, Any]]:
        """Generate LinkedIn-specific professional posts"""
        linkedin_templates = {
            'positive': [
                "Proud to announce {brand}'s latest achievement in {topic}. Our team's dedication continues to drive innovation.",
                "Excited to share {brand}'s success story in {service}. Thank you to our amazing clients and partners!",
                "Great to see {brand} recognized as a leader in {topic}. This motivates us to keep pushing boundaries.",
                "Another milestone reached! {brand}'s {service} has helped transform businesses across industries.",
                "Thrilled to celebrate {brand}'s growth and the incredible team that makes it all possible."
            ],
            'neutral': [
                "{brand} is participating in the upcoming {topic} conference. Looking forward to sharing insights.",
                "Interesting trends in {topic} that {brand} is closely monitoring. What are your thoughts?",
                "{brand} published a new whitepaper on {service} best practices. Link in comments.",
                "Join {brand}'s upcoming webinar on {topic} and digital transformation strategies.",
                "{brand} team is hiring! Looking for talented professionals in {topic} and {service}."
            ],
            'negative': [
                "Addressing recent challenges in {topic} - {brand} is committed to continuous improvement.",
                "Learning from feedback on our {service} offering. Your input helps us grow.",
                "Acknowledging the {topic} concerns raised by our community. We're working on solutions.",
                "{brand} is taking steps to enhance our {service} based on recent feedback.",
                "Transparency update: {brand} is addressing the {topic} issues reported last week."
            ]
        }
        
        posts = []
        
        # LinkedIn has more positive/neutral content
        positive_ratio = min(0.8, overall_sentiment + 0.1)
        negative_ratio = max(0.05, 0.8 - overall_sentiment)
        neutral_ratio = 1.0 - positive_ratio - negative_ratio
        
        for i in range(post_count):
            rand_val = random.random()
            if rand_val < positive_ratio:
                post_type = 'positive'
                post_sentiment = random.uniform(0.7, 0.95)
            elif rand_val < positive_ratio + neutral_ratio:
                post_type = 'neutral'
                post_sentiment = random.uniform(0.45, 0.65)
            else:
                post_type = 'negative'
                post_sentiment = random.uniform(0.2, 0.4)
            
            template = random.choice(linkedin_templates[post_type])
            service = random.choice(['solutions', 'services', 'consulting', 'technology', 'expertise'])
            topic = random.choice(topics)
            
            post_text = template.format(
                brand=brand_name,
                service=service,
                topic=topic
            )
            
            # LinkedIn typically has higher engagement
            base_engagement = random.randint(20, 200)
            if post_type == 'positive':
                base_engagement *= random.uniform(2.0, 4.0)
            
            posts.append({
                "text": post_text,
                "sentiment": round(post_sentiment, 3),
                "engagement": int(base_engagement),
                "likes": int(base_engagement * 0.8),
                "shares": int(base_engagement * 0.15),
                "comments": int(base_engagement * 0.05),
                "date": (datetime.now() - timedelta(days=random.randint(1, 14))).isoformat(),
                "type": post_type,
                "platform": "linkedin"
            })
        
        return posts

# Global instance for easy access
mock_generator = SocialMediaMockGenerator() 
import yaml
from datetime import datetime
import os

class FunnelData:
    def __init__(self):
        self.title = "Marketing Funnel"
        self.stages = [
            {"name": "Awareness", "items": ["Social Media", "Google Ads", "Meta Ads"], "color": "#FF9999"},
            {"name": "Engagement", "items": ["Lead Magnets", "Blog Content", "Emails"], "color": "#FFCC99"},
            {"name": "Consideration", "items": ["Retargeting Ads", "Testimonials", "Webinar"], "color": "#FFFF99"},
            {"name": "Conversion", "items": ["Consultation", "Sign-Ups", "Offers"], "color": "#CCFF99"},
            {"name": "Retention", "items": ["Community", "Check-ins", "Referrals"], "color": "#99FF99"}
        ]
        self.descriptions = {
            "Awareness": {
                "long": "Top of funnel - where potential customers first discover your brand through various marketing channels.",
                "short": "Potential customers discover\nyour brand and offerings"
            },
            "Engagement": {
                "long": "Users begin interacting with your content and showing interest in your offerings.",
                "short": "Users interact with content\nand show initial interest"
            },
            "Consideration": {
                "long": "Prospects actively evaluate your solution against alternatives.",
                "short": "Prospects evaluate options\nand consider solutions"
            },
            "Conversion": {
                "long": "Users take desired actions, becoming customers through purchases or sign-ups.",
                "short": "Leads convert into\npaying customers"
            },
            "Retention": {
                "long": "Maintaining customer relationships and encouraging repeat business and referrals.",
                "short": "Keep customers engaged\nand encourage referrals"
            }
        }

    def save(self, filename=None):
        if filename is None:
            # Generate default filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_title = "".join(c for c in self.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_title}_{timestamp}.yaml"

        data = {
            'title': self.title,
            'stages': self.stages
        }
        
        with open(filename, 'w') as f:
            yaml.safe_dump(data, f, default_flow_style=False)
        return filename

    @classmethod
    def load(cls, filename):
        with open(filename, 'r') as f:
            data = yaml.safe_load(f)
        
        funnel = cls()
        funnel.title = data['title']
        funnel.stages = data['stages']
        return funnel 
#!/usr/bin/env python3
"""
Business-Context Sentiment Analyzer
Recalibrates sentiment analysis for executive decision-making
"""

import boto3
import json
import re
from typing import Dict, List, Any, Tuple
from datetime import datetime

class BusinessSentimentAnalyzer:
    """
    Business-focused sentiment analysis that considers:
    - Employee retention risk
    - Operational impact
    - Policy/compensation reactions
    - Leadership concerns
    """
    
    def __init__(self):
        self.comprehend = boto3.client('comprehend', region_name='us-east-1')
        
        # Business-critical negative indicators
        self.business_negative_signals = {
            'retention_risk': [
                'quit', 'quitting', 'leaving', 'left', 'done', 'fed up', 
                'looking for another job', 'job hunting', 'resignation',
                'last day', 'two weeks notice', 'better opportunities'
            ],
            'compensation_dissatisfaction': [
                'underpaid', 'unfair', 'joke', 'insulting', 'pathetic',
                'not enough', 'barely surviving', 'can\'t afford',
                'poverty wages', 'slave wages', 'rip off', 'shafted',
                'screwed over', 'getting screwed'
            ],
            'policy_backlash': [
                'stupid policy', 'ridiculous', 'makes no sense',
                'who thought this up', 'terrible decision',
                'management doesn\'t care', 'out of touch'
            ],
            'operational_concerns': [
                'unsafe', 'dangerous', 'injury', 'hurt', 'pain',
                'burnout', 'exhausted', 'overworked', 'understaffed',
                'impossible quotas', 'unrealistic expectations'
            ],
            'morale_issues': [
                'hate this place', 'toxic', 'depressing', 'soul crushing',
                'no respect', 'treated like garbage', 'dehumanizing',
                'don\'t care about us', 'just a number'
            ]
        }
        
        # Business-positive indicators (genuine satisfaction)
        self.business_positive_signals = {
            'genuine_satisfaction': [
                'love working here', 'great company', 'fair treatment',
                'good benefits', 'competitive pay', 'work-life balance',
                'supportive management', 'career growth', 'opportunities'
            ],
            'policy_approval': [
                'good change', 'finally', 'about time', 'step in right direction',
                'improvement', 'better than before', 'fair decision'
            ],
            'retention_positive': [
                'staying', 'committed', 'long-term', 'career here',
                'recommend working here', 'proud to work here'
            ]
        }
        
        # Context modifiers that change sentiment interpretation
        self.context_modifiers = {
            'sarcasm_indicators': [
                'yeah right', 'sure', 'of course', 'obviously',
                'great job', 'brilliant', 'genius move'
            ],
            'sympathy_expressions': [
                'sorry for', 'heart goes out', 'feel bad for',
                'sending hugs', 'thoughts and prayers'
            ],
            'solidarity_expressions': [
                'we\'re in this together', 'support each other',
                'stick together', 'have each other\'s backs'
            ]
        }
    
    def analyze_business_sentiment(self, text: str, context: str = 'general') -> Dict[str, Any]:
        """
        Analyze sentiment from business perspective.
        
        Args:
            text: Text to analyze
            context: Business context (compensation, policy, management, etc.)
        
        Returns:
            Business sentiment analysis with executive insights
        """
        
        # Get AWS Comprehend baseline
        aws_sentiment = self._get_aws_sentiment(text)
        
        # Apply business context analysis
        business_analysis = self._analyze_business_context(text, context)
        
        # Determine final business sentiment
        final_sentiment = self._determine_business_sentiment(
            text, aws_sentiment, business_analysis, context
        )
        
        return {
            'aws_sentiment': aws_sentiment,
            'business_sentiment': final_sentiment['sentiment'],
            'business_confidence': final_sentiment['confidence'],
            'business_reasoning': final_sentiment['reasoning'],
            'risk_indicators': business_analysis['risk_indicators'],
            'business_impact': final_sentiment['business_impact'],
            'executive_summary': final_sentiment['executive_summary'],
            'recommended_action': final_sentiment['recommended_action']
        }
    
    def _get_aws_sentiment(self, text: str) -> Dict[str, Any]:
        """Get baseline AWS Comprehend sentiment."""
        try:
            if len(text.encode('utf-8')) > 5000:
                text = text[:4000]
            
            response = self.comprehend.detect_sentiment(
                Text=text,
                LanguageCode='en'
            )
            
            return {
                'sentiment': response['Sentiment'],
                'confidence_scores': response['SentimentScore']
            }
        except Exception as e:
            return {
                'sentiment': 'NEUTRAL',
                'confidence_scores': {'Neutral': 0.5}
            }
    
    def _analyze_business_context(self, text: str, context: str) -> Dict[str, Any]:
        """Analyze text for business-critical indicators."""
        
        text_lower = text.lower()
        risk_indicators = []
        positive_indicators = []
        
        # Check for business-negative signals
        for category, signals in self.business_negative_signals.items():
            for signal in signals:
                if signal in text_lower:
                    risk_indicators.append({
                        'category': category,
                        'signal': signal,
                        'severity': self._assess_severity(signal, category)
                    })
        
        # Check for business-positive signals
        for category, signals in self.business_positive_signals.items():
            for signal in signals:
                if signal in text_lower:
                    positive_indicators.append({
                        'category': category,
                        'signal': signal,
                        'strength': self._assess_positive_strength(signal, category)
                    })
        
        # Check for context modifiers
        modifiers = []
        for modifier_type, indicators in self.context_modifiers.items():
            for indicator in indicators:
                if indicator in text_lower:
                    modifiers.append({
                        'type': modifier_type,
                        'indicator': indicator
                    })
        
        return {
            'risk_indicators': risk_indicators,
            'positive_indicators': positive_indicators,
            'context_modifiers': modifiers
        }
    
    def _assess_severity(self, signal: str, category: str) -> str:
        """Assess severity of negative business signal."""
        high_severity_signals = [
            'quit', 'quitting', 'leaving', 'resignation', 'hate this place',
            'toxic', 'unsafe', 'dangerous', 'injury'
        ]
        
        if signal in high_severity_signals:
            return 'HIGH'
        elif category in ['retention_risk', 'operational_concerns']:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _assess_positive_strength(self, signal: str, category: str) -> str:
        """Assess strength of positive business signal."""
        strong_signals = [
            'love working here', 'great company', 'recommend working here',
            'career growth', 'competitive pay'
        ]
        
        if signal in strong_signals:
            return 'STRONG'
        else:
            return 'MODERATE'
    
    def _determine_business_sentiment(self, text: str, aws_sentiment: Dict, 
                                   business_analysis: Dict, context: str) -> Dict[str, Any]:
        """Determine final business sentiment with executive reasoning."""
        
        risk_indicators = business_analysis['risk_indicators']
        positive_indicators = business_analysis['positive_indicators']
        modifiers = business_analysis['context_modifiers']
        
        # Calculate business risk score
        risk_score = 0
        for risk in risk_indicators:
            if risk['severity'] == 'HIGH':
                risk_score += 3
            elif risk['severity'] == 'MEDIUM':
                risk_score += 2
            else:
                risk_score += 1
        
        # Calculate positive score
        positive_score = 0
        for pos in positive_indicators:
            if pos['strength'] == 'STRONG':
                positive_score += 3
            else:
                positive_score += 2
        
        # Apply context modifiers
        sympathy_detected = any(m['type'] == 'sympathy_expressions' for m in modifiers)
        sarcasm_detected = any(m['type'] == 'sarcasm_indicators' for m in modifiers)
        
        # Business sentiment logic
        if risk_score >= 3:  # High business risk
            sentiment = 'BUSINESS_NEGATIVE'
            confidence = min(0.9, 0.6 + (risk_score * 0.1))
            business_impact = 'HIGH_RISK'
        elif risk_score >= 1 and positive_score == 0:  # Some risk, no positives
            sentiment = 'BUSINESS_NEGATIVE'
            confidence = 0.7
            business_impact = 'MEDIUM_RISK'
        elif positive_score >= 3 and risk_score == 0:  # Strong positives, no risk
            sentiment = 'BUSINESS_POSITIVE'
            confidence = 0.8
            business_impact = 'POSITIVE'
        elif sympathy_detected and risk_score > 0:  # Sympathy about problems = business negative
            sentiment = 'BUSINESS_NEGATIVE'
            confidence = 0.8
            business_impact = 'MEDIUM_RISK'
            
        else:  # Mixed or neutral
            if risk_score > positive_score:
                sentiment = 'BUSINESS_NEGATIVE'
                business_impact = 'MEDIUM_RISK'
            elif positive_score > risk_score:
                sentiment = 'BUSINESS_POSITIVE'
                business_impact = 'POSITIVE'
            else:
                sentiment = 'BUSINESS_NEUTRAL'
                business_impact = 'NEUTRAL'
            confidence = 0.6
        
        # Generate executive reasoning
        reasoning = self._generate_executive_reasoning(
            aws_sentiment, risk_indicators, positive_indicators, 
            modifiers, sentiment, context
        )
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            sentiment, risk_indicators, business_impact, context
        )
        
        # Recommend action
        recommended_action = self._recommend_action(
            sentiment, risk_indicators, business_impact, context
        )
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'business_impact': business_impact,
            'reasoning': reasoning,
            'executive_summary': executive_summary,
            'recommended_action': recommended_action
        }
    
    def _generate_executive_reasoning(self, aws_sentiment: Dict, risk_indicators: List,
                                   positive_indicators: List, modifiers: List,
                                   final_sentiment: str, context: str) -> str:
        """Generate executive-level reasoning for sentiment classification."""
        
        reasoning_parts = []
        
        # AWS vs Business sentiment comparison
        aws_sent = aws_sentiment['sentiment']
        if aws_sent != final_sentiment.replace('BUSINESS_', ''):
            reasoning_parts.append(
                f"AWS classified as {aws_sent}, but business context indicates {final_sentiment}"
            )
        
        # Risk indicators
        if risk_indicators:
            high_risks = [r for r in risk_indicators if r['severity'] == 'HIGH']
            if high_risks:
                reasoning_parts.append(
                    f"HIGH RISK: Detected {len(high_risks)} critical business concerns"
                )
            
            retention_risks = [r for r in risk_indicators if r['category'] == 'retention_risk']
            if retention_risks:
                reasoning_parts.append(
                    f"Employee retention risk detected: {len(retention_risks)} indicators"
                )
        
        # Context modifiers
        sympathy = any(m['type'] == 'sympathy_expressions' for m in modifiers)
        if sympathy and risk_indicators:
            reasoning_parts.append(
                "Sympathy expressed about business problems = negative business impact"
            )
        
        return "; ".join(reasoning_parts) if reasoning_parts else "Standard sentiment analysis applied"
    
    def _generate_executive_summary(self, sentiment: str, risk_indicators: List,
                                  business_impact: str, context: str) -> str:
        """Generate executive summary of business implications."""
        
        if sentiment == 'BUSINESS_NEGATIVE':
            if business_impact == 'HIGH_RISK':
                return f"CRITICAL: Employee expressing serious concerns about {context}. Immediate attention required."
            else:
                return f"CONCERN: Negative employee sentiment about {context}. Monitor and address."
        
        elif sentiment == 'BUSINESS_POSITIVE':
            return f"POSITIVE: Employee satisfaction with {context}. Continue current approach."
        
        else:
            return f"NEUTRAL: Mixed or unclear sentiment about {context}. Monitor for trends."
    
    def _recommend_action(self, sentiment: str, risk_indicators: List,
                        business_impact: str, context: str) -> str:
        """Recommend executive action based on analysis."""
        
        if business_impact == 'HIGH_RISK':
            return "IMMEDIATE ACTION: Address employee concerns, review policies, consider retention measures"
        
        elif business_impact == 'MEDIUM_RISK':
            return "MONITOR: Track sentiment trends, prepare response if issues escalate"
        
        elif business_impact == 'POSITIVE':
            return "MAINTAIN: Continue successful practices, consider expanding positive initiatives"
        
        else:
            return "OBSERVE: Continue monitoring, no immediate action required"

def analyze_example_post():
    """Analyze the white badge post with business context."""
    
    analyzer = BusinessSentimentAnalyzer()
    
    post_text = """
    I'm sorry you guys are getting shafted the hardest today with the whole 50 cent raise shit today. 
    Especially anybody who's been a white badge for awhile, my heart goes out to all of you and I'm sending virtual hugs. 
    Whether this is a breaking point causing anybody to leave or not. There's always brighter skies ahead. 
    And higher paying jobs out there, but no matter what happens. Do not give up.
    """
    
    result = analyzer.analyze_business_sentiment(post_text, context='compensation')
    
    print("🎯 Business Sentiment Analysis Results")
    print("=" * 50)
    print(f"AWS Sentiment: {result['aws_sentiment']['sentiment']}")
    print(f"Business Sentiment: {result['business_sentiment']}")
    print(f"Business Confidence: {result['business_confidence']:.2f}")
    print(f"Business Impact: {result['business_impact']}")
    print()
    print("Executive Summary:")
    print(result['executive_summary'])
    print()
    print("Reasoning:")
    print(result['business_reasoning'])
    print()
    print("Recommended Action:")
    print(result['recommended_action'])
    print()
    print("Risk Indicators:")
    for risk in result['risk_indicators']:
        print(f"- {risk['category']}: '{risk['signal']}' (Severity: {risk['severity']})")

if __name__ == "__main__":
    analyze_example_post()
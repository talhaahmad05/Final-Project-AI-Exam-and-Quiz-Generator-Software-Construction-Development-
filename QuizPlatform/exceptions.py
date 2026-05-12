"""
filename: exceptions.py
module: Custom Exceptions
author: Talha Ahmad
date: 2026-05-12
"""

class QuizPlatformError(Exception):
    """Base exception for the Quiz Platform"""
    pass

class QuizAuthError(QuizPlatformError):
    """Raised when authentication fails"""
    pass

class QuizValidationError(QuizPlatformError):
    """Raised when form validation fails"""
    pass

class QuizDatabaseError(QuizPlatformError):
    """Raised when a database operation fails"""
    pass

class QuizAIError(QuizPlatformError):
    """Raised when an AI service call fails or returns malformed data"""
    pass

class QuizExamError(QuizPlatformError):
    """Raised for exam-related logical errors"""
    pass

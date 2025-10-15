from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from datetime import date

class User(BaseModel):
    uid: str
    email: EmailStr
    role: str  # "founder" | "investor"
    name: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class TeamMember(BaseModel):
    id: str
    name: str
    role: str
    experience: Optional[str]


class Milestone(BaseModel):
    date: date
    title: str
    description: Optional[str]


class Traction(BaseModel):
    users: Optional[str]
    revenue: Optional[str]
    growth: Optional[str]
    partnerships: List[str] = []
    milestones: List[Milestone] = []


class Product(BaseModel):
    description: Optional[str]
    features: List[str] = []
    marketSize: Optional[str]
    targetMarket: Optional[str]
    competitiveAdvantage: Optional[str]


class PreviousRound(BaseModel):
    round: str
    amount: str
    date: date
    investors: List[str] = []


class Financials(BaseModel):
    currentRunway: Optional[str]
    burnRate: Optional[str]
    seeking: Optional[str]
    valuation: Optional[str]
    previousRounds: List[PreviousRound] = []


class Risk(BaseModel):
    type: str = Field(..., regex="^(market|competitive|technical|regulatory|other)$")
    title: str
    description: Optional[str]
    severity: str = Field(..., regex="^(low|medium|high)$")


class Analysis(BaseModel):
    analysisId: str
    status: str
    filePath: str
    name: str
    description: Optional[str]
    industry: str
    stage: str
    foundedYear: Optional[int]
    lastUpdated: Optional[date]

    team: List[TeamMember] = []
    product: Product
    traction: Traction
    financials: Financials
    risks: List[Risk] = []

    # 👇 keep old fields for pipeline tracking
    userId: Optional[str]
    fileId: Optional[str]
    createdAt: Optional[str]
    updatedAt: Optional[str]

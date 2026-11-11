import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    profile = db.relationship(
        "UserProfile",
        backref="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    health_assessment = db.relationship(
        "HealthAssessment",
        backref="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    plans = db.relationship(
        "GeneratedPlan",
        backref="user",
        cascade="all, delete-orphan",
        order_by="desc(GeneratedPlan.generated_at)"
    )
    history = db.relationship(
        "PlanHistory",
        backref="user",
        cascade="all, delete-orphan",
        order_by="desc(PlanHistory.created_at)"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def friend_code(self):
        return f"FIT-{self.id:04d}"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "friend_code": self.friend_code,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class UserProfile(db.Model):
    __tablename__ = "user_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )
    age = db.Column(db.Float, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    height = db.Column(db.Float, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    fitness_goal = db.Column(db.String(50), default="general_fitness")
    fitness_level = db.Column(db.String(50), default="beginner")
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            "name": self.user.name if self.user else "",
            "age": self.age,
            "gender": self.gender,
            "height": self.height,
            "weight": self.weight,
            "fitness_goal": self.fitness_goal or "general_fitness",
            "fitness_level": self.fitness_level or "beginner",
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class HealthAssessment(db.Model):
    __tablename__ = "health_assessments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )
    selected_conditions = db.Column(db.Text, nullable=True)  # JSON-encoded array
    previous_surgery = db.Column(db.Boolean, default=False)
    affected_body_part = db.Column(db.String(120), nullable=True)
    surgery_date = db.Column(db.String(50), nullable=True)
    medically_cleared = db.Column(db.Boolean, default=False)
    additional_information = db.Column(db.Text, nullable=True)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def get_conditions_list(self):
        if not self.selected_conditions:
            return []
        try:
            return json.loads(self.selected_conditions)
        except Exception:
            return [c.strip() for c in self.selected_conditions.split(",") if c.strip()]

    def set_conditions_list(self, conditions):
        if isinstance(conditions, list):
            self.selected_conditions = json.dumps(conditions)
        elif isinstance(conditions, str):
            self.selected_conditions = conditions
        else:
            self.selected_conditions = json.dumps([])

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "selected_conditions": self.get_conditions_list(),
            "previous_surgery": bool(self.previous_surgery),
            "affected_body_part": self.affected_body_part or "",
            "surgery_date": self.surgery_date or "",
            "medically_cleared": bool(self.medically_cleared),
            "additional_information": self.additional_information or "",
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class GeneratedPlan(db.Model):
    __tablename__ = "generated_plans"

    id = db.Column(db.String(64), primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    plan_type = db.Column(db.String(50), nullable=False)
    goal = db.Column(db.String(50), nullable=False)
    fitness_level = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    equipment = db.Column(db.String(50), nullable=True)
    body_part = db.Column(db.String(50), nullable=True)
    plan_data = db.Column(db.Text().with_variant(MEDIUMTEXT(), "mysql"), nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_plan_json(self):
        if isinstance(self.plan_data, dict):
            return self.plan_data
        try:
            return json.loads(self.plan_data)
        except Exception:
            return {}

    def to_dict(self):
        return {
            "id": self.id,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
            "plan_type": self.plan_type,
            "goal": self.goal,
            "fitness_level": self.fitness_level,
            "duration": self.duration,
            "equipment": self.equipment,
            "body_part": self.body_part,
            "plan": self.get_plan_json()
        }


class PlanHistory(db.Model):
    __tablename__ = "plan_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    plan_id = db.Column(db.String(64), nullable=True)
    activity = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Optional relationship to GeneratedPlan
    plan = db.relationship(
        "GeneratedPlan",
        primaryjoin="foreign(PlanHistory.plan_id) == GeneratedPlan.id",
        uselist=False,
        lazy="joined"
    )

    def to_dict(self):
        plan_ref = self.plan
        return {
            "id": self.plan_id or str(self.id),
            "history_id": self.id,
            "plan_id": self.plan_id,
            "activity": self.activity or "Generated Fitness Plan",
            "plan_type": plan_ref.plan_type if plan_ref else (self.activity or "Fitness"),
            "goal": plan_ref.goal if plan_ref else "—",
            "fitness_level": plan_ref.fitness_level if plan_ref else "—",
            "duration": plan_ref.duration if plan_ref else "—",
            "generated_at": (
                plan_ref.generated_at.isoformat()
                if (plan_ref and plan_ref.generated_at)
                else (self.created_at.isoformat() if self.created_at else None)
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class UserFriendship(db.Model):
    __tablename__ = "user_friendships"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    friend_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    status = db.Column(db.String(20), default="accepted")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("user_id", "friend_id", name="uq_user_friend"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "friend_id": self.friend_id,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class FriendKudos(db.Model):
    __tablename__ = "friend_kudos"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    recipient_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    message = db.Column(db.String(120), default="sent you a High Five! ✦")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship("User", foreign_keys=[sender_id])

    def to_dict(self):
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "sender_name": self.sender.name if self.sender else "Friend",
            "message": self.message,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

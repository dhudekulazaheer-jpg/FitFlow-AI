"""
Smart Warm-Up & Cool-Down Protocol Module for FitFlow AI
Provides dynamic, scientifically aligned 3-minute warm-up prep
and 3-minute restorative cool-down stretches.
"""

def get_warmup_cooldown(body_part=None, is_yoga=False, goal="general_fitness"):
    body_part_norm = str(body_part).lower().strip() if body_part else "full_body"
    goal_norm = str(goal).lower().strip()

    # Dynamic Warm-Up Protocols (3 minutes total)
    if is_yoga or goal_norm == "flexibility":
        warmup = [
            {
                "sequence": 1,
                "name": "Cat-Cow Dynamic Spinal Waves",
                "duration_seconds": 60,
                "target": "Spine & Core",
                "instructions": "Inhale to arch your back, lifting your chest (Cow); exhale to round the spine toward the ceiling (Cat). Move mindfully with breath."
            },
            {
                "sequence": 2,
                "name": "Standing Side Stretch & Arm Sweeps",
                "duration_seconds": 60,
                "target": "Intercostals & Shoulders",
                "instructions": "Reach arms overhead, clasp wrists and gently lean side-to-side to open the lateral line and expand breathing capacity."
            },
            {
                "sequence": 3,
                "name": "Gentle Sun Salutation Prep",
                "duration_seconds": 60,
                "target": "Full Body Circulation",
                "instructions": "Flow gently between Mountain Pose, Half Forward Fold, and Plank to elevate body temperature and lubricate synovial joints."
            }
        ]
    elif body_part_norm in ["lower legs", "upper legs", "waist"]:
        warmup = [
            {
                "sequence": 1,
                "name": "Dynamic Leg Swings & Hip Openers",
                "duration_seconds": 60,
                "target": "Hips & Hamstrings",
                "instructions": "Hold a wall for balance and swing one leg forward and back smoothly, then switch. Open the hip flexors."
            },
            {
                "sequence": 2,
                "name": "Bodyweight Air Squats & Calf Raises",
                "duration_seconds": 60,
                "target": "Quadriceps & Calves",
                "instructions": "Perform slow, controlled air squats focusing on hip depth, pressing onto toes at the top to awaken calves."
            },
            {
                "sequence": 3,
                "name": "Glute Bridge Activations",
                "duration_seconds": 60,
                "target": "Glutes & Posterior Chain",
                "instructions": "Lie on back with knees bent, squeeze glutes at the top of the bridge for 2 seconds. Drive blood to the posterior chain."
            }
        ]
    else:  # Upper body / chest / back / arms / full body
        warmup = [
            {
                "sequence": 1,
                "name": "Arm Circles & Chest Expansions",
                "duration_seconds": 60,
                "target": "Rotator Cuff & Pectorals",
                "instructions": "Begin with small forward circles, gradually widening. Reverse directions, then open arms wide to gently stretch the chest."
            },
            {
                "sequence": 2,
                "name": "Torso Twists & Shoulder Rolls",
                "duration_seconds": 60,
                "target": "Thoracic Spine & Deltoids",
                "instructions": "Rotate your torso left and right with relaxed arms, pivoting on the back foot. Roll shoulders smoothly backwards."
            },
            {
                "sequence": 3,
                "name": "Inchworm Walkouts",
                "duration_seconds": 60,
                "target": "Core, Shoulders & Hamstrings",
                "instructions": "Hinge at the hips, place hands on the floor, walk out to a plank position, hold 2 seconds, and walk hands back to standing."
            }
        ]

    # Restorative Cool-Down Protocols (3 minutes total)
    if is_yoga or goal_norm == "flexibility":
        cooldown = [
            {
                "sequence": 1,
                "name": "Balasana (Child's Pose)",
                "duration_seconds": 60,
                "target": "Lower Back & Hips",
                "instructions": "Kneel, open knees wide, bring big toes together, and walk hands forward resting forehead on the mat. Surrender body weight."
            },
            {
                "sequence": 2,
                "name": "Supta Matsyendrasana (Supine Spinal Twist)",
                "duration_seconds": 60,
                "target": "Spine & Glutes",
                "instructions": "Lie on back, hug knees to chest, and drop both knees to one side while gazing toward opposite fingertips. Breathe deep into belly."
            },
            {
                "sequence": 3,
                "name": "Savasana & Diaphragmatic Breathwork",
                "duration_seconds": 60,
                "target": "Parasympathetic Reset",
                "instructions": "Rest completely flat on your back, relax your jaw, shoulders, and hips. Inhale for 4 seconds, exhale slowly for 6 seconds."
            }
        ]
    elif body_part_norm in ["lower legs", "upper legs", "waist"]:
        cooldown = [
            {
                "sequence": 1,
                "name": "Standing Quad & Hip Flexor Stretch",
                "duration_seconds": 60,
                "target": "Quadriceps",
                "instructions": "Hold ankle behind you, tuck tailbone slightly, and pull heel towards glute. Hold 30 seconds per side."
            },
            {
                "sequence": 2,
                "name": "Seated Forward Fold & Hamstring Release",
                "duration_seconds": 60,
                "target": "Hamstrings & Lower Back",
                "instructions": "Sit tall with legs straight ahead. Hinge from the hips and reach towards toes with a soft bend in knees. Breathe out tension."
            },
            {
                "sequence": 3,
                "name": "Wall-Supported Calf & Achilles Stretch",
                "duration_seconds": 60,
                "target": "Gastrocnemius & Soleus",
                "instructions": "Step one foot back, press rear heel firmly into the ground, and lean into the wall. Switch legs after 30 seconds."
            }
        ]
    else:  # Upper body / full body
        cooldown = [
            {
                "sequence": 1,
                "name": "Cross-Body Shoulder & Deltoid Stretch",
                "duration_seconds": 60,
                "target": "Posterior Deltoids & Triceps",
                "instructions": "Bring right arm across your chest, gently draw it inward with left forearm. Keep shoulders down. Switch after 30 seconds."
            },
            {
                "sequence": 2,
                "name": "Doorway / Wall Pectoral Opener",
                "duration_seconds": 60,
                "target": "Chest & Biceps",
                "instructions": "Place forearm against a doorframe at 90 degrees, step forward gently until a deep stretch is felt in the chest and front shoulder."
            },
            {
                "sequence": 3,
                "name": "Deep Diaphragmatic Breathing Reset",
                "duration_seconds": 60,
                "target": "Autonomic Nervous System",
                "instructions": "Place one hand on chest and one on abdomen. Inhale deep into your lower belly for 4 seconds, hold 2, exhale slow for 6."
            }
        ]

    return {
        "warmup": warmup,
        "cooldown": cooldown,
        "protocol_note": "A 3-minute dynamic warm-up primes muscle motor units, and a 3-minute cool-down accelerates lactic clearance."
    }

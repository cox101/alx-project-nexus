from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Poll, Option, Vote

User = get_user_model()


class OptionSerializer(serializers.ModelSerializer):
    vote_count = serializers.SerializerMethodField()
    vote_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Option
        fields = ['id', 'text', 'vote_count', 'vote_percentage']

    def get_vote_count(self, obj):
        return obj.vote_count

    def get_vote_percentage(self, obj):
        return obj.vote_percentage


class PollListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for poll lists"""
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    status = serializers.CharField(read_only=True)
    total_votes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Poll
        fields = [
            'id', 'title', 'description', 'created_by_username', 
            'created_at', 'start_time', 'end_time', 'status', 'total_votes'
        ]


class PollDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer with options for poll detail view"""
    options = OptionSerializer(many=True, read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    status = serializers.CharField(read_only=True)
    total_votes = serializers.IntegerField(read_only=True)
    has_expired = serializers.BooleanField(read_only=True)
    has_started = serializers.BooleanField(read_only=True)
    is_currently_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Poll
        fields = [
            'id', 'title', 'description', 'created_by', 'created_by_username',
            'created_at', 'updated_at', 'start_time', 'end_time',
            'is_active', 'allow_multiple_votes', 'is_anonymous',
            'status', 'total_votes', 'has_expired', 'has_started', 
            'is_currently_active', 'options'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class CreatePollSerializer(serializers.ModelSerializer):
    options = serializers.ListField(
        child=serializers.CharField(max_length=255),
        write_only=True,
        min_length=2,
        help_text="List of option texts for the poll"
    )

    class Meta:
        model = Poll
        fields = [
            'title', 'description', 'start_time', 'end_time', 
            'is_active', 'allow_multiple_votes', 'is_anonymous', 'options'
        ]

    def validate(self, data):
        # Validate time fields
        if data.get('start_time') and data.get('end_time'):
            if data['start_time'] >= data['end_time']:
                raise serializers.ValidationError("End time must be after start time.")
        
        # Validate future end time for new polls
        if data.get('end_time') and data['end_time'] <= timezone.now():
            raise serializers.ValidationError("End time must be in the future.")
        
        return data

    def validate_options(self, value):
        # Remove duplicates while preserving order
        seen = set()
        unique_options = []
        for option in value:
            option = option.strip()
            if option and option.lower() not in seen:
                seen.add(option.lower())
                unique_options.append(option)
        
        if len(unique_options) < 2:
            raise serializers.ValidationError("At least 2 unique options are required.")
        
        return unique_options

    def create(self, validated_data):
        options_data = validated_data.pop('options')
        user = self.context['request'].user
        poll = Poll.objects.create(created_by=user, **validated_data)
        
        # Create options
        Option.objects.bulk_create([
            Option(poll=poll, text=option_text) 
            for option_text in options_data
        ])
        
        return poll


class UpdatePollSerializer(serializers.ModelSerializer):
    """Serializer for updating polls (limited fields)"""
    
    class Meta:
        model = Poll
        fields = ['title', 'description', 'end_time', 'is_active']

    def validate_end_time(self, value):
        if value and value <= timezone.now():
            raise serializers.ValidationError("End time must be in the future.")
        return value


class VoteSerializer(serializers.ModelSerializer):
    option_text = serializers.CharField(source='option.text', read_only=True)
    poll_title = serializers.CharField(source='poll.title', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Vote
        fields = ['id', 'poll', 'option', 'user', 'voted_at', 'option_text', 'poll_title', 'username']
        read_only_fields = ['user', 'voted_at', 'poll']

    def validate(self, data):
        request = self.context.get('request')
        user = request.user if request else None
        option = data.get('option')
        
        if not option:
            raise serializers.ValidationError("Option is required.")
        
        poll = option.poll
        
        # Check if poll is currently active
        if not poll.is_currently_active:
            raise serializers.ValidationError("This poll is not currently accepting votes.")
        
        # Check if user has already voted (unless multiple votes allowed)
        if user and not poll.allow_multiple_votes:
            existing_vote = Vote.objects.filter(poll=poll, user=user).exists()
            if existing_vote:
                raise serializers.ValidationError("You have already voted on this poll.")
        
        return data

    def create(self, validated_data):
        # Set user from request context
        validated_data['user'] = self.context['request'].user
        # Set poll from option
        validated_data['poll'] = validated_data['option'].poll
        return super().create(validated_data)


class CreateVoteSerializer(serializers.Serializer):
    """Simplified serializer for creating votes"""
    option_id = serializers.IntegerField()

    def validate_option_id(self, value):
        try:
            option = Option.objects.get(id=value)
        except Option.DoesNotExist:
            raise serializers.ValidationError("Invalid option ID.")
        
        poll = option.poll
        
        # Check if poll is active
        if not poll.is_currently_active:
            raise serializers.ValidationError("This poll is not currently accepting votes.")
        
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        option = Option.objects.get(id=validated_data['option_id'])
        poll = option.poll
        
        # Check for existing vote
        if not poll.allow_multiple_votes:
            if Vote.objects.filter(poll=poll, user=user).exists():
                raise serializers.ValidationError("You have already voted on this poll.")
        
        vote = Vote.objects.create(
            user=user,
            option=option,
            poll=poll
        )
        
        return vote


class PollResultsSerializer(serializers.ModelSerializer):
    """Serializer for poll results"""
    options = OptionSerializer(many=True, read_only=True)
    total_votes = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Poll
        fields = ['id', 'title', 'description', 'total_votes', 'options', 'end_time']


class UserVoteSerializer(serializers.ModelSerializer):
    """Serializer for user's voting history"""
    poll_title = serializers.CharField(source='poll.title', read_only=True)
    option_text = serializers.CharField(source='option.text', read_only=True)
    
    class Meta:
        model = Vote
        fields = ['id', 'poll_title', 'option_text', 'voted_at']
        read_only_fields = ['id', 'poll_title', 'option_text', 'voted_at']


class PollSerializer(serializers.ModelSerializer):
    """Serializer for the Poll model"""
    
    class Meta:
        model = Poll
        fields = ['id', 'title', 'description', 'options', 'is_active', 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

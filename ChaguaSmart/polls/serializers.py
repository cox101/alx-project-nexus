from rest_framework import serializers
from django.utils import timezone
from .models import Poll, Option, Vote


class OptionSerializer(serializers.ModelSerializer):
    votes_count = serializers.IntegerField(source='votes.count', read_only=True)

    class Meta:
        model = Option
        fields = ['id', 'text', 'votes_count']


class PollSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)
    has_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = Poll
        fields = ['id', 'title', 'description', 'created_by', 'created_at', 'expiry_date', 'has_expired', 'options']
        read_only_fields = ['created_by', 'created_at']


class CreatePollSerializer(serializers.ModelSerializer):
    options = serializers.ListField(
        child=serializers.CharField(max_length=255),
        write_only=True,
        min_length=2
    )

    class Meta:
        model = Poll
        fields = ['title', 'description', 'expiry_date', 'options']

    def create(self, validated_data):
        options = validated_data.pop('options')
        user = self.context['request'].user
        poll = Poll.objects.create(created_by=user, **validated_data)
        Option.objects.bulk_create([Option(poll=poll, text=opt) for opt in options])
        return poll


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['poll', 'option', 'user', 'voted_at']
        read_only_fields = ['user', 'voted_at']

    def validate(self, data):
        poll = data['poll']
        if poll.has_expired:
            raise serializers.ValidationError("Poll has expired.")
        return data

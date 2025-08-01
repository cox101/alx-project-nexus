from rest_framework import serializers
from .models import Poll, Option, Vote


class OptionSerializer(serializers.ModelSerializer):
    vote_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Option
        fields = ['id', 'option_text', 'vote_count']
    
    def get_vote_count(self, obj):
        return obj.vote_set.count()


class PollSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)
    total_votes = serializers.SerializerMethodField()
    
    class Meta:
        model = Poll
        fields = [
            'id', 
            'title', 
            'description', 
            'start_time', 
            'end_time', 
            'created_by',
            'options',
            'total_votes'
        ]
    
    def get_total_votes(self, obj):
        return Vote.objects.filter(option__poll=obj).count()


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'option', 'user', 'voted_at']
        read_only_fields = ['user', 'voted_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PollCreateSerializer(serializers.ModelSerializer):
    options = serializers.ListField(
        child=serializers.CharField(max_length=255),
        write_only=True,
        min_length=2
    )
    
    class Meta:
        model = Poll
        fields = ['title', 'description', 'start_time', 'end_time', 'options']
    
    def create(self, validated_data):
        options_data = validated_data.pop('options')
        poll = Poll.objects.create(**validated_data)
        
        for option_text in options_data:
            Option.objects.create(poll=poll, option_text=option_text)
        
        return poll
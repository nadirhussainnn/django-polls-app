import random
from django.views import generic
from django.shortcuts import render, get_object_or_404, redirect

from polls.models import Poll, Question, Choice

class PollListView(generic.ListView):
    model = Poll
    template_name = "polls/index.html"     
    context_object_name = "polls"

    def get_queryset(self):
        return Poll.objects.select_related().all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        image_list = ["icons1.png", "icons2.png", "icons3.png", "icons4.png", "icons5.png"]

        for poll in context["polls"]:
            poll.random_image = random.choice(image_list)

            if poll.is_expired():
                first_question = poll.question_set.first()
                if first_question:
                    top_choice = first_question.choice_set.order_by("-votes").first()
                else:
                    top_choice = None
                
                poll.winner_choice = top_choice
            else:
                poll.winner_choice = None

        return context


class DetailView(generic.DetailView):
    model = Poll
    template_name = "polls/details.html"


class ResultsView(generic.DetailView):
    model = Poll
    template_name = "polls/results.html"


def vote(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    
    if request.method != "POST":
        return redirect("detail", poll_id=poll.id)

    try:
        question_id = int(request.POST["question_id"])
        choice_id = int(request.POST["choice"])

        question = poll.question_set.get(id=question_id)
        selected_choice = question.choice_set.get(id=choice_id)

    except (KeyError, ValueError, Question.DoesNotExist, Choice.DoesNotExist):
        context = {
            "poll": poll,
            "error_message": "You didn't select a valid choice.",
        }
        return render(request, "polls/details.html", context)

    # Increment vote
    selected_choice.votes += 1
    selected_choice.save()

    # Redirect to results page (PRG pattern)
    return redirect("results", pk=poll.id)
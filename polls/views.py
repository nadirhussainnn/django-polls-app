import random
from django.shortcuts import render, get_object_or_404, redirect

from polls.models import Poll, Question, Choice


def index(request):
    polls = Poll.objects.select_related().all()
    image_list = ["icons1.png", "icons2.png", "icons3.png", "icons4.png", "icons5.png"]
    for poll in polls:
        poll.random_image = random.choice(image_list)
        
    return render(request, "polls/index.html", {"polls": polls})


def detail(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    return render(request, "polls/details.html", {"poll": poll})


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
    return redirect("results", poll_id=poll.id)


def results(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    return render(request, "polls/results.html", {"poll": poll})
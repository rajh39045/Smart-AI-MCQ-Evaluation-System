class Evaluator:

    def evaluate(self, answer_key, student_answers):
        """
        Compare answer key with student answers.

        Parameters
        ----------
        answer_key : dict
            Example:
            {
                "1":"A",
                "2":"B",
                "3":"D"
            }

        student_answers : dict
            Example:
            {
                "1":"A",
                "2":"C",
                "3":"D"
            }

        Returns
        -------
        dict
        """

        total = len(answer_key)

        correct = 0
        wrong = 0
        unanswered = 0

        details = {}

        for question, correct_answer in answer_key.items():

            student_answer = student_answers.get(question)

            # Question not attempted
            if student_answer is None:

                unanswered += 1

                details[question] = {
                    "correct_answer": correct_answer,
                    "student_answer": "-",
                    "status": "UNANSWERED"
                }

            # Correct Answer
            elif student_answer == correct_answer:

                correct += 1

                details[question] = {
                    "correct_answer": correct_answer,
                    "student_answer": student_answer,
                    "status": "CORRECT"
                }

            # Wrong Answer
            else:

                wrong += 1

                details[question] = {
                    "correct_answer": correct_answer,
                    "student_answer": student_answer,
                    "status": "WRONG"
                }

        percentage = 0

        if total > 0:
            percentage = round((correct / total) * 100, 2)

        return {

            "total_questions": total,

            "correct": correct,

            "wrong": wrong,

            "unanswered": unanswered,

            "score": correct,

            "percentage": percentage,

            "details": details
        }
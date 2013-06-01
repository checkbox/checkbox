#ifndef STEP_H
#define STEP_H

#include <QWidget>

class Step : public QWidget
{
public:
    Step(QWidget *parent, QString text = "", QString index = "");
    ~Step();
};

#endif // STEP_H

#include <QHBoxLayout>
#include <QGraphicsScene>
#include <QGraphicsEllipseItem>
#include <QGraphicsView>
#include <QGraphicsTextItem>
#include <QLabel>

#include "step.h"

#define STEP_COLOR "#DD3814"

Step::Step(QWidget *parent, QString text, QString index)
{
    setParent(parent);
    setFixedWidth(470);
    QHBoxLayout *layout = new QHBoxLayout(this);

    if (index != "") {
        QGraphicsScene *scene = new QGraphicsScene(0, 0, 20, 20);
        QGraphicsEllipseItem *item = new QGraphicsEllipseItem(0, 0, 20, 20);
        item->setBrush(QBrush(STEP_COLOR));
        item->setPos(0,0);
        scene->addItem(item);
        item->setPos(0,0);
        QGraphicsView *view = new QGraphicsView(scene);
        view->setRenderHint(QPainter::Antialiasing, true);
        view->setRenderHint(QPainter::TextAntialiasing, true);
        view->setFrameShape(QFrame::NoFrame);
        view->setBackgroundRole(QPalette::NoRole);
        view->setFixedSize(20, 20);
        QGraphicsTextItem *text = new QGraphicsTextItem(item, scene);
        text->setHtml("<center>"+index+"</center>");
        text->setPos(1,-2);
        text->setTextWidth(18);
        layout->addWidget(view);
    } else {
        QWidget *widget = new QWidget(this);
        widget->setFixedWidth(50);
        layout->addWidget(widget);
    }

    QLabel *label = new QLabel(text);
    label->setWordWrap(true);
    label->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Maximum);
    layout->addWidget(label);
    show();

}

Step::~Step() {
    hide();
}

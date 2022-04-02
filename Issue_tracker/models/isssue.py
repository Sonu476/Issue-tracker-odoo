from odoo import fields, models, _
from datetime import datetime


class ManageIssues(models.Model):
    _name = "manage.issue"
    _rec_name = 'issue_name'

    def _compute_comment_count(self):
        for rec in self:
            comment_count = self.env['resolve.issue'].search_count([('issue_id', '=', rec.id)])
            rec.comment_count = comment_count

    def _compute_status(self):
        for rec in self:
            comment_string  = self.env['resolve.issue'].search([('issue_id', '=', rec.id),('comment','=','fixed')]).comment
            print(comment_string)
            rec.Is_resolved = comment_string

    Is_resolved = fields.Boolean('Is_resolved', compute='_compute_status')
    print(Is_resolved);
    print("fixed")
    state = fields.Selection([('open', 'Open'), ('close', 'Close')],default='open',
                             string="Status", tracking=True)
    comment_count = fields.Integer(compute='_compute_comment_count')
    issue_name = fields.Char(string='Issue Name', track_visibility=True)
    comment_lines = fields.One2many('resolve.issue', 'issue_id', string="comment_line")

    def action_open(self):
        for rec in self:
            self.env['resolve.issue'].search([('issue_id', '=', rec.id),('comment','=','fixed')]).write({'comment':'Re_open'})
            rec.state = 'open'

    def action_close(self):
        for rec in self:
            if rec.Is_resolved:
                rec.state = 'close'
            else:
                message = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Warning!'),
                        'message': 'cannot close issue since it is not fixed',
                        'sticky': False,
                    }
                }
                return message

    def action_open_comments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Comments',
            'res_model': 'resolve.issue',
            'domain': [('issue_id', '=', self.id)],
            'context': {'default_issue_id': self.id},
            'view_mode': 'tree,form',
            'target': 'current',
        }


class ResolveIssue(models.Model):
    _name = "resolve.issue"
    _rec_name = "comment"

    issue_id = fields.Many2one("manage.issue", string="Issue Name")
    comment = fields.Text(string='Comment')
    email_id = fields.Many2one('res.users','Login', default=lambda self: int(self.env.uid))
    comment_date = fields.Datetime(string="Latest authentication", default=lambda self: fields.datetime.now())



